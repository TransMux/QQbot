import time
from pathlib import Path
from typing import Union

import pandas as pd
from gocqapi import api
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg
from nonebot.permission import SUPERUSER

member_list = on_command("群列表", priority=5, permission=SUPERUSER)


@member_list.handle()
async def handle_first_receive(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()  # 首次发送命令时跟随的参数，例：/天气 上海，则args为上海
    if plain_text:
        matcher.set_arg("group_id", args)  # 如果用户发送了参数则直接赋值


@member_list.got("group_id", prompt="你想查询哪个群呢？")
async def handle_city(event: Union[PrivateMessageEvent, GroupMessageEvent], city_name: str = ArgPlainText("group_id")):
    file = await get_members(city_name)
    await api.upload_group_file(event.group_id, file, str(file), None)
    await member_list.finish("执行成功")


async def get_members(group_id: str) -> Path:
    members = await api.get_group_member_list(group_id)
    members = [m.dict() for m in members]
    members_df = pd.DataFrame(members)
    # group_id date member_list
    date = time.strftime("%Y-%m-%d", time.localtime())
    file_name = Path(f"群成员列表 {date} {group_id}.xlsx")
    # to xlsx
    members_df.to_excel(file_name, index=False)
    return file_name
