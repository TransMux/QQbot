from nonebot import get_bot, on_command
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.params import ArgPlainText, CommandArg
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me

member_list = on_command("群列表", rule=to_me(), priority=5, permission=SUPERUSER)


@member_list.handle()
async def handle_first_receive(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()  # 首次发送命令时跟随的参数，例：/天气 上海，则args为上海
    if plain_text:
        matcher.set_arg("group_id", args)  # 如果用户发送了参数则直接赋值


@member_list.got("group_id", prompt="你想查询哪个群呢？")
async def handle_city(city_name: str = ArgPlainText("group_id")):
    members = await get_members(city_name)
    await member_list.finish(members)


# 在这里编写获取天气信息的函数
async def get_members(group_id: str) -> str:
    bot = get_bot()
    members = await bot.call_api('get_group_member_list', group_id=group_id)
    # extract card from members list
    card_list = [member["card"] for member in members]
    return "\n".join(card_list)
