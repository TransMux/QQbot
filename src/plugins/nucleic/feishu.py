import json
import time

import requests
from cacheout import Cache

token_cache = Cache(maxsize=256, ttl=60 * 60, timer=time.time, default=None)  # defaults
data_cache = Cache(maxsize=256, ttl=30, timer=time.time, default=None)  # defaults

@token_cache.memoize()
def token():
    payload = json.dumps({
        "app_id": "cli_a39311354b7c9013",
        "app_secret": "2laxjT3frIxaPIQse2L3gbjwOaE7IJZD"
    })
    r = requests.request(
        "POST", "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        headers={
            'Content-Type': 'application/json'
        }, data=payload
    ).json()
    return r["tenant_access_token"]


def get_all_data():
    has_more = True
    page_token = ""
    headers = {
        'Authorization': 'Bearer ' + token()
    }
    all_data = []
    while has_more:
        print(page_token)
        url = "https://open.feishu.cn/open-apis/bitable/v1/apps/bascnQmR309dXpImddq2u7gzRqe/tables/tblL8RDy96cwVdCe" \
              "/records?page_size=300&view_id=vewIr83vQU&page_token=" + page_token
        r = requests.request("GET", url, headers=headers).json()
        all_data.extend(r["data"]["items"])
        has_more = r["data"]["has_more"]
        page_token = r["data"]["page_token"]

    return all_data


def post_process(raw):
    all_data = []
    for item in raw:
        all_data.append({
            "姓名": item["fields"]["姓名"],
            "学号": item["fields"]["学号"],
            "班级": item["fields"]["班级"],
            "填报状态": item["fields"]["是否完成今日核酸检测"][0]["text"],
        })

    return all_data

@data_cache.memoize()
def get_sheet_data():
    import pandas as pd
    all_data = post_process(get_all_data())
    df = pd.DataFrame(all_data)
    return df


if __name__ == '__main__':
    data = get_sheet_data()
    data = data[data["填报状态"] == "未填报"]
    report = "未填报同学名单：\n\n"
    for class_id, class_data in data.groupby("班级"):
        report += f"{class_id}：\n"
        for name in class_data["姓名"]:
            report += f"    {name}\n"
    print(report)
