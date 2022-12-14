import requests
import time
from datetime import datetime
import asyncio

import config


def get_emails_from_user_list(users):
    emails = []
    for user in users:
        emails.append(user[1])
    print(" ".join(emails))
    return emails


async def get_users(group_id: int) -> list:
    url = f"https://ahmadullin.getcourse.ru/pl/api/account/groups/{group_id}/users"
    params = {"key": config.gk_key, }
    response = requests.get(url, params=params)
    json_resp = response.json()
    if json_resp['success']:
        export_id = json_resp['info']['export_id']
    print(export_id)
    wait_time = 10

    url2 = f"https://ahmadullin.getcourse.ru/pl/api/account/exports/{export_id}"
    while True:
        response2 = requests.get(url2, params=params)
        print("request...", wait_time)
        r = response2.json()
        if not r['success']:
            await asyncio.sleep(wait_time)
            wait_time += 10
        else:
            return get_emails_from_user_list(r["info"]["items"])
