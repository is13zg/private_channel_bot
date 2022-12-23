from create_bot import bot

async def big_send(chat_id, content, sep="\n"):
    reply = sep.join(content)
    while (len(reply) > 4096):
        x = reply[:4096]
        i = x.rfind(sep)
        await bot.send_message(chat_id, x[:i])
        reply = reply[i:]
    if len(reply) > 0:
        await bot.send_message(chat_id, reply)



