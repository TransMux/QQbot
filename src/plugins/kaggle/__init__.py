import time

from src.plugins.kaggle.api import 获取Leaderboard, 保存今天和昨天的分数计数汇总, competition

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler



scheduler.add_job(获取Leaderboard, "cron", hour=6, minute=0, second=0)

scheduler.add_job(保存今天和昨天的分数计数汇总, "cron", hour=6, minute=30, second=0)

async def 发送汇总图片():
    file = competition + " " + time.strftime("%Y-%m-%d") + ".png"
    bot = get_bot()
    await api.upload_group_file("563922968", file, file, None)

scheduler.add_job(发送汇总图片, "cron", hour=7, minute=00, second=0)
