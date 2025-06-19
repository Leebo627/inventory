import json
import time
import mysql.connector
import pandas as pd
import requests
import datetime


def get_tenant_id():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"

    payload = 'app_id=cli_a68bf6d33338100b&app_secret=io3StwprLI9I7FmfJaneZeKPzA5rCSfN'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'is_anonymous_session=; sl_session=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTE0MDIwODcsInVuaXQiOiJldV9uYyIsInJhdyI6eyJtZXRhIjoiQVdYUnVLQWRSQUFFWWF4QktzTUFnQnhsL09mZVZFREFCR1g4NTk1VVFNQUVaZnpvQkIyb1FBUUNLZ0VBUVVGQlFVRkJRVUZCUVVKc0wwOW5SVXhCVVVGQ1FUMDkiLCJzdW0iOiJkODFiYjE0ZTcyYTIwMDBlYzIxNTNjOTAwMDEyMGI5ZTVjMGQ5MmQwMzVkMjAxZWQ5OWNjMTE3YTZiYjQyNWZmIiwibG9jIjoiemhfY24iLCJhcGMiOiJSZWxlYXNlIiwiaWF0IjoxNzExMzU4ODg3LCJzYWMiOnsiVXNlclN0YWZmU3RhdHVzIjoiMSIsIlVzZXJUeXBlIjoiNDIifSwibG9kIjpudWxsLCJucyI6ImxhcmsiLCJuc191aWQiOiI3MzM2ODQ4MjY1Nzg4NTIyNTAwIiwibnNfdGlkIjoiNzAzODA3MTk2OTU4OTI2NDQxMiIsIm90IjoxfX0.nM8ohaPk3qCR_KMsT_vZ0xiLGEC-Csc5GpYaWC2xH-iMpKIGJtwvOjz63NsqEep_wQsCu5eDDDIahrV1QRaDSA'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response = response.text
    response = dict(json.loads(response))
    tenant_token = response.get('tenant_access_token')
    return tenant_token

def get_sheet_overseas(token,sheet,table,view):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{sheet}/tables/{table}/records/search"

    payload = json.dumps({
        "view_id": view,
        "page_size": 1000
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % token,
        'Cookie': '_csrf_token=538176cf9383ceb63b6ef0de8d359c3b30c2eb5e-1715666196'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.text)
    result = json.loads(response.text).get('data')
    result = dict(result).get('items')
    return result


if __name__ == '__main__':

    sheet = 'VEGnbUM8KaH2a0sv7YGcc8IHnJc'  # 同步数据源

    table_overseas_overduce = 'tblubH2ZUGBqjKaT'


    view_overseas_overduce = 'vewpUfrngm'


    tenant_token = get_tenant_id()
    df_sheet_overseas = get_sheet_overseas(tenant_token,sheet,table_overseas_overduce,view_overseas_overduce)
    for info in df_sheet_overseas:
        data_part =[]
        info = dict(info).get('fields')
        age_20_30 = info['20-30天']
        if age_20_30 != 0:
            asin_overduce =  dict(info).get('asin')[0]['text']
            category = dict(info).get('品线')
            data_part.append(asin_overduce)

        print(info)
