import time
from pathlib import Path
from typing import Union

from gocqapi import api
from nonebot import on_command, require
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg

from src.plugins.nucleic.feishu import get_sheet_data

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

report_raw_table = on_command("核酸填报详细名单", priority=5)


@report_raw_table.handle()
async def handle_first_receive(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()  # 首次发送命令时跟随的参数，例：/天气 上海，则args为上海
    if plain_text:
        matcher.set_arg("class_id", args)  # 如果用户发送了参数则直接赋值


@report_raw_table.got("class_id", prompt="您需要查询哪个班？")
async def handle_city(class_id: str = ArgPlainText("class_id")):
    data = get_sheet_data()
    data = data[data["填报状态"] == "未填报"]
    report = "未填报同学名单：\n\n"
    for current_class, class_data in data.groupby("班级"):
        if (class_id in current_class) or class_id == "全部":
            report += f"{current_class}：\n"
            for name in class_data["姓名"]:
                report += f"    {name}\n"
    print(report)

    await report_raw_table.finish(report)


async def send_all_scheduled():
    data = get_sheet_data()
    data = data[data["填报状态"] == "未填报"]
    report = "核酸未填报同学：\n\n"
    for current_class, class_data in data.groupby("班级"):
        report += f"{current_class}：\n"
        for name in class_data["姓名"]:
            report += f"    {name}\n"
    print(report)

    await api.send_msg(report, user_id=1563881250)
    await api.send_msg(report, user_id=774326857)
    await api.send_msg(report, user_id=2294227991)
    await api.send_msg(report, group_id=559735949)
    await api.send_msg(report, group_id=745109536)


scheduler.add_job(send_all_scheduled, "cron", hour=11, minute=45, second=0)

scheduler.add_job(send_all_scheduled, "cron", hour=11, minute=55, second=0)

scheduler.add_job(send_all_scheduled, "cron", hour=12, minute=5, second=0)


# 核酸填报情况汇总

report_summary = on_command("核酸填报情况汇总", priority=5)


@report_summary.handle()
async def handle_first_receive():
    data = get_sheet_data()
    # Count
    all_count = data.shape[0]
    finished_count = data[data["填报状态"] == "已填报"].shape[0]
    unfinished_count = data[data["填报状态"] == "未填报"].shape[0]
    # Summary
    report = f"2020级当前在校人数{all_count}人，今日核酸检测已完成{finished_count}人，{unfinished_count}人未完成，正在一对一督促。"

    await report_summary.finish(report)


async def report_scheduled():
    data = get_sheet_data()
    # Count
    all_count = data.shape[0]
    finished_count = data[data["填报状态"] == "已填报"].shape[0]
    unfinished_count = data[data["填报状态"] == "未填报"].shape[0]
    # Summary
    report = f"2020级当前在校人数{all_count}人，今日核酸检测已完成{finished_count}人，{unfinished_count}人未完成，正在一对一督促。"
    await api.send_msg(report, user_id=1563881250)
    await api.send_msg(report, user_id=774326857)
    await api.send_msg(report, user_id=2294227991)


scheduler.add_job(report_scheduled, "cron", hour=11, minute=50, second=0)

scheduler.add_job(report_scheduled, "cron", hour=12, minute=0, second=0)

scheduler.add_job(report_scheduled, "cron", hour=12, minute=10, second=0)

# 核酸填报表

all_table_raw = on_command("核酸填报表", priority=5)


@all_table_raw.handle()
async def handle_first_receive(event: Union[PrivateMessageEvent, GroupMessageEvent]):
    data = get_sheet_data()
    # group_id date member_list
    date = time.strftime("%Y-%m-%d", time.localtime())
    file_name = Path(f"核酸填报表 {date}.xlsx")
    # to xlsx
    data.to_excel(file_name, index=False)
    await api.upload_group_file(event.group_id, file_name, str(file_name), None)
