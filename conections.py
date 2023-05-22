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


async def get_users(group_ids: int | list):
    print("start")
    if type(group_ids) not in [int, list]:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, "group_id no int no list")
        return
    if type(group_ids) == int:
        group_ids = [group_ids]

    all_mails = []
    for group_id in group_ids:
        print(group_id)

        url = f"https://ahmadullin.getcourse.ru/pl/api/account/groups/{group_id}/users"
        params = {"key": config.gk_key, }
        response = requests.get(url, params=params)
        json_resp = response.json()
        print(json_resp)
        if json_resp['success']:
            export_id = json_resp['info']['export_id']
            print(json_resp)
        else:
            await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name,
                                                f"No export id, resp={response.text}")
            return None

        print(export_id)
        wait_time = 30
        print("need wait", wait_time)
        await asyncio.sleep(wait_time)
        print("wait finish")

        url2 = f"https://ahmadullin.getcourse.ru/pl/api/account/exports/{export_id}"

        while True:
            response2 = requests.get(url2, params=params)
            print("request...", wait_time)
            r = response2.json()
            print(r)
            if not r['success']:
                wait_time += 30
                print("need wait", wait_time)
                await asyncio.sleep(wait_time)
                print("wait finish")
                await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, r)
            else:
                all_mails.extend(get_emails_from_user_list(r["info"]["items"]))
                break
    return all_mails
