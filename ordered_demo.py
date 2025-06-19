import random
import re
import pandas as pd
from anaconda_project.internal.conda_api import result
from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import requests
import hmac
import hashlib
import base64
import datetime
import time
import uuid
import concurrent.futures
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import warnings
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

def get_sheet(token):
    url = "https://open.feishu.cn/open-apis/bitable/v1/apps/VEGnbUM8KaH2a0sv7YGcc8IHnJc/tables/tblx07vC1UBGxuoG/records/search"

    payload = json.dumps({
        "view_id": "vewqQCcLoJ" # 已下单未发货
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

tenant_token = get_tenant_id()
df_sheet = get_sheet(tenant_token)
print(result)