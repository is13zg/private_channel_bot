import requests
import asyncio
import create_bot
import config
import inspect


def get_emails_from_user_list(users):
    emails = []
    for user in users:
        emails.append(user[1])
    # print(" ".join(emails))
    return emails


async def get_users(group_id: int):
    if type(group_id) != int:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, "group_id no int")
        return

    url = f"https://ahmadullin.getcourse.ru/pl/api/account/groups/{group_id}/users"
    params = {"key": config.gk_key, }
    response = requests.get(url, params=params)
    json_resp = response.json()
    if json_resp['success']:
        export_id = json_resp['info']['export_id']
    else:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name,
                                            f"No export id, resp={response.text}")
        return None

    # print(export_id)
    wait_time = 30
    await asyncio.sleep(wait_time)

    url2 = f"https://ahmadullin.getcourse.ru/pl/api/account/exports/{export_id}"
    while True:
        response2 = requests.get(url2, params=params)
        print("request...", wait_time)
        r = response2.json()
        # print(r)
        if not r['success']:
            wait_time += 10
            await asyncio.sleep(wait_time)
            await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, r)
        else:
            return get_emails_from_user_list(r["info"]["items"])
