import json
import time
from gc import freeze
from http.client import responses

import mysql.connector
import pandas as pd
import requests
import datetime

# 创建新数据 插入新asin时使用
def mysql_input(data):
    # 连接到MySQL数据库
    conn = mysql.connector.connect(
        host="rm-bp1a33e3ww3pdfcnvso.mysql.rds.aliyuncs.com",
        user="Blaise",
        password="Libo20020627!",
        database="eastoak_inventory"
    )
    cursor = conn.cursor()
    # 插入数据
    sql = (
        "INSERT INTO inventory (ASIN, catagory, asin_name, inventory_all, amzOpenPurchase, amzsallable, amzonPO,amzon_po_di, amz_on_po_do,outsea_used_PO,outsea_sellable_PO,  outsea_on_DO,amz_di_waiting_ship,date_update,sku,qty_recieved,over_age_num,ordered_waitingforship) VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
    cursor.execute(sql, data)

    # 提交事务
    conn.commit()
    # 关闭连接
    cursor.close()
    conn.close()


def mysql_upsert(data):
    conn = mysql.connector.connect(
        host="rm-bp1a33e3ww3pdfcnvso.mysql.rds.aliyuncs.com",
        user="Blaise",
        password="Libo20020627!",
        database="eastoak_inventory"
    )
    cursor = conn.cursor()

    sql = """
    INSERT INTO inventory 
        (ASIN, catagory, asin_name, inventory_all, amzOpenPurchase, amzsallable, 
         amzonPO, amzon_po_di, amz_on_po_do, outsea_used_PO, outsea_sellable_PO, 
         outsea_on_DO, amz_di_waiting_ship, date_update, sku, qty_recieved, 
         over_age_num, ordered_waitingforship) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
        inventory_all = VALUES(inventory_all),
        amzOpenPurchase = VALUES(amzOpenPurchase),
        amzsallable = VALUES(amzsallable),
        amzonPO = VALUES(amzonPO),
        amzon_po_di = VALUES(amzon_po_di),
        amz_on_po_do = VALUES(amz_on_po_do),
        outsea_used_PO = VALUES(outsea_used_PO),
        outsea_sellable_PO = VALUES(outsea_sellable_PO),
        outsea_on_DO = VALUES(outsea_on_DO),
        amz_di_waiting_ship = VALUES(amz_di_waiting_ship),
        sku = VALUES(sku),
        qty_recieved = VALUES(qty_recieved),
        over_age_num = VALUES(over_age_num),
        ordered_waitingforship = VALUES(ordered_waitingforship)
    """

    cursor.execute(sql, data)
    conn.commit()
    cursor.close()
    conn.close()

# 更新旧数据
def mysql_data_update(data):
    conn = mysql.connector.connect(
        host="rm-bp1a33e3ww3pdfcnvso.mysql.rds.aliyuncs.com",
        user="Blaise",
        password="Libo20020627!",
        database="eastoak_inventory"
    )
    cursor = conn.cursor()
    sql = "UPDATE inventory SET inventory_all=%s, amzOpenPurchase=%s, amzsallable=%s, amzonPO=%s,amzon_po_di=%s, amz_on_po_do=%s,outsea_used_PO=%s,outsea_sellable_PO=%s, outsea_on_DO=%s,amz_di_waiting_ship=%s,date_update=%s,sku=%s,qty_recieved=%s,over_age_num=%s,ordered_waitingforship=%s WHERE ASIN = %s"
    cursor.execute(sql, data)
    # 提交事务
    conn.commit()
    # 关闭连接
    cursor.close()
    conn.close()


# # 创建数据库表函数 初始化时使用
# def create_mysql_table():
#     # 连接到MySQL数据库
#     conn = mysql.connector.connect(
#         host="rm-bp1a33e3ww3pdfcnvso.mysql.rds.aliyuncs.com",
#         user="Blaise",
#         password="Libo20020627!",
#         database="eastoak_inventory"
#     )
#     cursor = conn.cursor()
#     # 插入数据
#     sql = """CREATE TABLE your_table (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(255),age INT,email VARCHAR(255))"""
#     # 提交事务
#     cursor.execute(sql)
#     conn.commit()
#     # 关闭连接
#     cursor.close()
#     conn.close()

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

# 从path中读取sellable on hand units数据
def get_amz_avaibletoSale(path):
    info_result = []
    df = pd.read_excel(path)
    df.fillna(0, inplace=True)
    for index, row in df.iterrows():
        info_result_part = []
        asin = row['ASIN']
        # 亚马逊可售 = Sellable On Hand Units - Unfilled Customer Ordered Units
        sellable_on_hand_units = row['Sellable On Hand Units']
        unfilled_customer_ordered_units = row['Unfilled Customer Ordered Units']
        amz_avaibletoSale =sellable_on_hand_units - unfilled_customer_ordered_units
        # 超期库存
        over_age_num = row['Aged 90+ Days Sellable Units']
        info_result_part.append(asin)
        info_result_part.append(amz_avaibletoSale)
        info_result_part.append(over_age_num)
        info_result.append(info_result_part)
    return info_result

# 从path中读取Open Purchase Order Quantity数据
def get_open_purchase(path):
    info_result = []
    df = pd.read_excel(path)
    df.fillna(0, inplace=True)
    for index, row in df.iterrows():
        info_result_part = []
        asin = row['ASIN']
        open_purchase_quantity = row['Open Purchase Order Quantity']
        info_result_part.append(asin)
        info_result_part.append(open_purchase_quantity)
        info_result.append(info_result_part)
    return info_result


#调用上边自定义方法获取亚马逊可售数据
# def get_open_purchase(date, asin_list, headers):
#     info_result = []
#     for i in range(0, len(asin_list), 100):
#         if i + 100 >= len(asin_list):
#             result = data_source_vc_open_purchase(date, asin_list[i:len(asin_list)], headers)
#         else:
#             result = data_source_vc_open_purchase(date, asin_list[i:i + 100], headers)
#             time.sleep(1)
#         for info in result:
#             info_result_part = []
#             asin = info[0].get('value')
#             open_purchase_quantity = info[7].get('value')
#             info_result_part.append(asin)
#             info_result_part.append(open_purchase_quantity)
#             info_result.append(info_result_part)
#     return info_result


# vc后台 在途数据


# sevc海外仓占用po数量
def out_sea_inventory(header, page):
    url = "https://api.spotterio.com/spotter-warehouse-web/sevc/inventory/warehouse/page"
    payload = json.dumps({
        "pageSize": 1000,
        'filterZeroFlag':0,
        "currentPage": page,
        "sortQuery": {}
    })
    headers = header
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.status_code)
    result = response.text
    # print('111')
    print(response.text)
    # print('222')
    result = json.loads(result)
    result = result.get('data').get('data')
    return result

# 获取特定Asin和月份的PO数据
def fetch_data_for_asin_and_month(asin, month, year, headers, result_inner):
    url = "https://vendorcentral.amazon.com/po-api/vendor/members/po-mgmt/search/search"
    payload = json.dumps({
        "searchTerm": asin,
        "searchYear": "%s" % year,
        "isConfirmed": True,
        "isClosed": False,
        "month": month,
        "paginatedRequest": {
            "lastEvaluatedKey": None
        }
    })
    headers = headers
    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        print("--->", response.status_code)
        print("--->", response.text)
        print("__________________")
        result = dict(response.json()).get('paginatedResponse').get('payload')
        qty_outstanding_di = 0  # 总di在途和待发
        qty_open_purchase_di = 0  # Accepted quantity 我们反馈的接收数量
        qty_outstanding_do = 0  # 总do在途
        qty_open_purchase_do = 0  # Accepted quantity 我们反馈的接收数量
        qty_on_ship_di = 0
        qty_received_outstanding_di = 0
        for info in result:
            vendor = info.get('vendor')
            if vendor.endswith('H'):  # H结尾且有quantity代表有do在途
                qty_open_purchase_do += info.get('totalCases')
                qty_outstanding_do += info.get('qtyOutstanding')
            else:  # di在途
                # 如果是di的
                # 先得到接收的数量 qtyReceived>0,说明接收中，就不算在途，对应的po qtyOutstanding就是接收中的数量
                qty_received = int(info.get('qtyReceived'))
                qty_open_purchase_di += info.get('totalCases')
                if qty_received <= 0 and info.get('qtyOutstanding') > 0:  # 若没有接收的数量且outstanding>0的说明是待发和在途
                    qty_outstanding_di += info.get('qtyOutstanding')  # 待发和在途的数量
                    po_id_di = info.get('poId')  # 把poId拿过来去看是不是在途
                    df_di_info = result_inner[result_inner['PO #'] == po_id_di][result_inner['ASIN #'] == asin]['ETD']
                    if len(df_di_info) > 0:
                        df_di_info = df_di_info.values[0]
                    else:
                        df_di_info = 0
                    if df_di_info != 0 and df_di_info < pd.to_datetime(datetime.datetime.today().date()):
                        qty_on_ship_di += \
                            sum(result_inner[result_inner['PO #'] == po_id_di][result_inner['ASIN #'] == asin][
                                    'Case\nQty'].values)*sum(result_inner[result_inner['PO #'] == po_id_di][result_inner['ASIN #'] == asin][
                                    'Case\nPack'].values)
                    else:
                        qty_on_ship_di += 0
                else:
                    qty_received_outstanding_di += info.get('qtyOutstanding')

        return qty_outstanding_di, qty_open_purchase_di, qty_outstanding_do, qty_open_purchase_do, qty_received_outstanding_di, qty_on_ship_di

# 获取所有Asin和月份的PO数据
def fetch_data_for_all_asins_and_months(headers, asin, result_inner):
    qty_outstanding_all_di = 0
    qty_open_purchase_all_di = 0
    qty_outstanding_all_do = 0
    qty_open_purchase_all_do = 0
    qty_outstanding_all_di_on_ship = 0
    qty_outstanding_all_di_received = 0
    data_part = []
    print(asin)
    for year in range(2024, 2026):  # 跨年修改
        for month in range(1, 13):
            # 调用上边方法遍历获取所有asin对应的PO数据
            try:
                qty_outstanding_di, qty_open_purchase_di, qty_outstanding_do, qty_open_purchase_do, qty_received_outstanding_di, qty_on_ship_di = fetch_data_for_asin_and_month(
                    asin, month, year, headers, result_inner)
            except Exception:
                flag = 1
                while True:
                    time.sleep(3)
                    if flag == 5:
                        break
                    try:
                        qty_outstanding_di, qty_open_purchase_di, qty_outstanding_do, qty_open_purchase_do, qty_received_outstanding_di, qty_on_ship_di = fetch_data_for_asin_and_month(
                            asin, month, year, headers, result_inner)
                        break
                    except Exception as e:
                        print(e)
            print(qty_on_ship_di)
            print(qty_outstanding_all_di_on_ship)
            # di的outstanding被分成了接收中和在途两部分
            qty_outstanding_all_di += qty_outstanding_di  # 这部分的di为在途和待发加起来的数量
            qty_open_purchase_all_di += qty_open_purchase_di
            qty_outstanding_all_do += qty_outstanding_do  # do不用管
            qty_open_purchase_all_do += qty_open_purchase_do
            qty_outstanding_all_di_on_ship += qty_on_ship_di  # 根据di物流表找到的di在途的数量
            qty_outstanding_all_di_received += qty_received_outstanding_di  # 接受中的数量
    data_part.append(asin)
    data_part.append(qty_outstanding_all_di)
    data_part.append(qty_open_purchase_all_di)
    data_part.append(qty_outstanding_all_do)
    data_part.append(qty_open_purchase_all_do)
    data_part.append(qty_outstanding_all_di_on_ship)
    data_part.append(qty_outstanding_all_di_received)
    return data_part


# sevc确认中
# 获取sevc货物情况
def approving_ship_units(asin, header):
    url = 'https://api.spotterio.com/spotter-warehouse-web/sevc/inventory/warehouse/page'
    payload = json.dumps({
        "currentPage": 1,
        "filterZeroFlag":"0",
        "keyword": "%s" % asin,
        "pageSize": 20,
        "sortQuery": {}
})

    headers = header
    time.sleep(0.5)
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        result = dict(json.loads(response.text)).get('data').get('data')
    else:
        print(f"访问失败:{response.text}")
    return result


def approving_ship_units_result(link, spt_number):
    url = 'https://bi-out.spotterio.com/api/embed/dashboard/%s/dashcard/4300/card/3361?ssku=%s' % (link, spt_number)

    payload = json.dumps({
        "ssku" : "%s" % spt_number
    })

    headers = {
        'Accept':'application/json',
        'Accept-encoding':'gzip,eflate,br,zstd',
        'Accept-language':'zh-CN,zh;q=0.9',
        'Content-type':'application/json',
        'Cookie':spotter_cookie,
        'Priority':'u=1,i',
        'Referer':'https://bi-out.spotterio.com/embed/dashboard/%s?'%link,
        'Sec-ch-ua':'"Google Chrome";v="131", "Chromium";v = "131", "Not_A Brand";v = "24"',
        'Sec-ch-ua-mobile':'?0',
        'Sec-ch-ua-platform':'"Windows"',
        'Sec-fetch-dest':'empty'
    }


    response = requests.request("GET", url, headers=headers)
    # result = dict(json.loads(response.text)).get('data').get('orderItemVOList')
    # print(response.text)
    result = dict(json.loads(response.text)).get('data').get('rows')
    return result

# 获取API信息 确保访问海外库存报告时URL都是正确的
def get_api_info_amount_all_sevc():
    url = "https://bi-auth.spotterio.com/api/v1/biurl/sevc/get-url/501"

    payload = {}
    headers = {
        'accept':'*/*',
        'accept-encoding':'gzip, deflate, br, zstd',
        'accept-language':'zh-CN,zh;q=0.9',
        'cookie':spotter_cookie,
        'if-none-match':'W/"110-s3c9aYwesmal6fUDgIw3k4C73nY"',
        'origin':'https://sevc.spotterio.com',
        'priority':'u=1, i',
        'referer':'https://sevc.spotterio.com/',
        'sec-ch-ua':'"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'sec-fetch-dest':'empty',
        'sec-fetch-mode':'cors',
        'sec-fetch-site':'same-site',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'x-site-tenant':'US_AMZ'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code != 200:
        print(f"访问API信息失败：{response.status_code}")

    return response.text

# sevc 运输中
# 获取sevc货物情况
def shipping_units(asin, header):
    # url = "https://api.spotterio.com/spotter-ess-web/sevc/spt/order/page"
    # payload = json.dumps({
    #     "currentPage": 1,
    #     "pageSize": 10000,
    #     "status": "3",
    #     "keyword": "%s" % asin,
    #     "sortQuery": {},
    #     "createdAtBeginMs": 1685602800000,
    #     "createdAtEndMs": 1751439599999,
    #     "shippingWay": None
    # })
    url = "https://api.spotterio.com/spotter-warehouse-web/sevc/warehouse/outbound/page"
    payload = json.dumps({

        "currentPage": 1,
        "pageSize": 10000,
        "keyword":"%s" % asin,
        "status": "3",
        "sortQuery": {
            "column": "createdDateMs",
            "sortType": "descend"
        },
        "createdDateMsStart": 1725951600000,
        "createdDateMsEnd": 1731311999999,
        "shippingWay": None
    })
    headers = header
    time.sleep(0.5)
    response = requests.request("POST", url, headers=headers, data=payload)
    result = dict(json.loads(response.text)).get('data').get('data')
    return result


def shipping_units_result(spt_number, header):

    # url = "https://api.spotterio.com/spotter-ess-web/sevc/spt/order/detail"
    # payload = json.dumps({
    #     "shipmentOrderCode": "%s" % spt_number
    # })

    url = "https://api.spotterio.com/spotter-warehouse-web/sevc/warehouse/outbound/page"
    payload = json.dumps({
        "currentPage": 1,
        "pageSize": 1000,
        "sortQuery": {
            "column": "createdDateMs",
            "sortType": "descend"
        },
        "outboundNo": "%s" % spt_number,
        "createdDateMsStart": 1726297200000,
        "createdDateMsEnd": 1731657599999
    })

    headers = header

    response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.text)
    # result = dict(json.loads(response.text)).get('data').get('orderItemVOList')
    result = dict(json.loads(response.text)).get('data').get('data')
    return result


# 获取sevc库存数据
def df_inventory(asin,headers_spotter):

    url = 'https://api.spotterio.com/spotter-warehouse-web/sevc/inventory/warehouse/page'
    payload = json.dumps({
      "pageSize": 10000,
      "currentPage": 1,
      "keyword": "%s" % asin,
      "sortQuery": {}
})
    headers = headers_spotter
    response = requests.request("POST", url, headers=headers, data=payload)
    result = json.loads(response.text)
    result = result.get('data').get('data')
    return result

def get_WaitDeliverNum_all(sku,storageCode):
    url = "https://api.spotterio.com/spotter-warehouse-web/sevc/inventory/warehouse/sku/occupy/list"
    payload = json.dumps({
        "storageCode": storageCode,
        "ssku": sku
    })
    headers = headers_spotter
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        result = json.loads(response.text)
        result = result.get('data').get('records')
    else:
        print(f"占用库存访问失败：{response.status_code}")

    return result

if __name__ == '__main__':

    # asin sku列表
    df_asin = pd.read_excel("【运营中心】AsinList_Asin List 登记表_【别动-引用的】主表.xlsx")

    tenant_token = get_tenant_id()

    df_sheet = get_sheet(tenant_token)

    # 标题项列表
    # data = [['ASIN', '品线', '产品名称', '总库存', '亚马逊OpenPurchase', '1.亚马逊可售','1.1超期库存', '2.亚马逊在途PO',
    #          '2.1亚马逊在途po(di)', '2.2亚马逊在途po(do)', '2.2.1海外仓占用PO',
    #          '3.海外仓可售PO', '4.海运在途DO', '5.亚马逊po(di)待发','6.已下单未发货']]

    # asin列表
    asin_all = ['B099NTY7WL', 'B09M8DJ41Y', 'B09MJK3LBH', 'B09MJK7SJQ', 'B09Q39SJYK', 'B09Q39ZY44',
                'B09Q3CN4NF', 'B09RFVC6VN', 'B09RFYNJHN', 'B09RFZKZQF', 'B09RFZMV7Z', 'B09RG23ZKJ', 'B09RGRDFS4',
                'B09RJ1X26G', 'B09RJ37XRN', 'B09RJ3JKPP', 'B09RJ4QRDQ', 'B09SHCBW3L', 'B09SXXBHT1',
                'B09T3KK25X', 'B09T3M6J7F', 'B09T3MMZZN', 'B09T3N2YQF', 'B09T3NLMTM', 'B09T3NS545', 'B09VL3NVVV',
                'B09VL3ZLCS', 'B09VL4F5CV', 'B09VL4HZ8Y', 'B09VL4HZBB', 'B09VL5KSKP', 'B09VL62D2N', 'B09VL7MC62',
                'B09VL88ZWR', 'B09VL8JC4D', 'B09VX3F92Y', 'B09VX8JL4V', 'B09VXHZVV3',
                'B09VXKQ5FX', 'B09W31RHPP', 'B09W325QLR', 'B09W335V1R', 'B09W33GFQH', 'B09W33S13L',
                'B09W33VJFJ', 'B09W33W2YZ', 'B09W344S24', 'B09W34CFWD', 'B09W34DM1Z', 'B09W34F2L3', 'B09W34HDBH',
                'B0B1DQR99D', 'B0B1DQYWTR', 'B0B1DSK3N8', 'B0B9LCR8V1', 'B0B9LD1M25', 'B0B9LDHQ5L', 'B0B9LF7VFX',
                'B0B9LFFQ2C', 'B0B9LYVTF4', 'B0B9M11TDL', 'B0B9M1PB3T',
                'B0B9M1ZSNJ', 'B0B9M3FTM8', 'B0B9MKC9HD', 'B0B9MNHF8C', 'B0B9MNNXVW', 'B0B9MPY9T7',
                'B0B9RP8L81', 'B0B9RQGKBJ', 'B0B9RSTHZC', 'B0B9SLNDHS', 'B0B9SPMZTN', 'B0B9SRMCS9',
                'B0B9SZKV5P', 'B0B9T14MPK', 'B0B9T36L2L', 'B0B9T39HPV', 'B0B9T3ZNSP', 'B0B9T45CCL', 'B0B9T46GWC',
                'B0B9T53R47', 'B0B9T5JP7Q', 'B0B9T5MH7X', 'B0B9T5SHRY', 'B0B9T5YF53', 'B0B9T6FF18', 'B0B9T6FMP1',
                'B0B9T6VX4Z', 'B0BC41KW3V', 'B0BC457RS7', 'B0BC951PXL', 'B0BC963G33', 'B0BC98BGTV', 'B0BC98SM3T',
                'B0BC99N615', 'B0BC99NM5L', 'B0BC9B6DT9', 'B0BC9BC74P', 'B0BC9BM22G', 'B0BC9T92W8', 'B0BC9TDQ8F',
                'B0BC9TY2Z8', 'B0BC9VQSHM', 'B0BC9YHSGK', 'B0BC9YM2SF', 'B0BCD5TRWW', 'B0BCD93K3B', 'B0BCDW2VBK',
                'B0BCF9HG98', 'B0BCFK9R8V', 'B0BCGD4B77', 'B0BCKW6X6V', 'B0BD9YMB91', 'B0BDDHHK3B', 'B0BDF48RMS',
                'B0BDFHL3PD', 'B0BDFM6HG1', 'B0BDFSP8PJ', 'B0BDFVV4TM', 'B0BDG2RTBH', 'B0BDG4YW4J', 'B0BDG7V877',
                'B0BDGB3YRZ', 'B0BDGBPQ9X', 'B0BDGBPRQP', 'B0BDGDFLSH', 'B0BDGFYM9C', 'B0BDM3BDFS', 'B0BDM3LGF1',
                'B0BGKMDRY1', 'B0BGKRVS27', 'B0BGKSB2S4', 'B0BGKSKJ9G', 'B0BGKTGR3L', 'B0BGKVMS5P', 'B0BGKW1FVG',
                'B0BGKW1GS2', 'B0BGKW58NG', 'B0BGKW7TLR', 'B0BGKW86RV', 'B0BGKWCNY9', 'B0BGKWG929', 'B0BGKWHD9X',
                'B0BGKWHXVG', 'B0BGKWJ67V', 'B0BGKWV596', 'B0BGKXF9ZQ', 'B0BGKXGP7Z', 'B0BGKXTMGJ', 'B0BGKXW4DF',
                'B0BGKXZ919', 'B0BGKY8C11', 'B0BGLCBWHZ', 'B0BHWZLLPS', 'B0BND6WKG1', 'B0BND7616B', 'B0BND7CHPS',
                'B0BPM88GRT', 'B0BPQZQ8J1', 'B0BPQZZ1K3', 'B0BPR32B2R', 'B0BW982GD9', 'B0BZDFDNMJ', 'B0BZDFY9DM',
                'B0BZDGLZ9J', 'B0BZMYJMHZ', 'B0BZMZC213', 'B0BZN359N7', 'B0C1C5PTRV', 'B0C4THS9YL', 'B0C5ZVVPXG',
                'B0C6TH952K', 'B0C6THVMTS', 'B0C6TJ8FJK', 'B0C6TJBKJM', 'B0C6TJHNKX', 'B0C6TJY9PQ', 'B0C6TJZTX8',
                'B0C6TK5P5Q', 'B0C6TKJ3H7', 'B0C783Q9N6', 'B0C7841GJM', 'B0C7CM31CP', 'B0C7CNCV32', 'B0C7CNTM2Y',
                'B0C7CQNZXB', 'B0CBSDGKFS', 'B0CBSDW6GD', 'B0CBSF4XF9', 'B0CBSFBT64', 'B0CBSFM7FF',
                'B0CBSFQX8S', 'B0CBSFSDCL', 'B0CBSFSX5G', 'B0CBSGVTVZ',
                'B0CC987TKN', 'B0CC98TY5C', 'B0CC9H9L1Y', 'B0CC9KJMRM', 'B0CC9KQMXT', 'B0CCMV7VJL', 'B0CCYT8JJQ',
                'B0CCYVSDBY', 'B0CDMBCZKL', 'B0CF54TBKY', 'B0CFXB1JGJ', 'B0CGDSN856', 'B0CGH6P433', 'B0CGVDCGXS',
                'B0CHRX4P96', 'B0CHYGT6KR', 'B0CJ2B3DJJ', 'B0CJ2CSHYW', 'B0CJ2DMHKV', 'B0CJ2FXHPN', 'B0CJ2GNYLH',
                'B0CJJM1FHK', 'B0CJTYCXGZ', 'B0CJV25K91', 'B0CKPGZX8K', 'B0CKQBFQJJ', 'B0CKQCY5TH', 'B0CKQD2DBN',
                'B0CKQD5XFN', 'B0CKQDJ3DV', 'B0CKQDKG87', 'B0CKQDTFZ6', 'B0CKQFMMY5', 'B0CKQTZHB7', 'B0CKSV8ZKS',
                'B0CLC8GTFF', 'B0CLCW5M4H', 'B0CLD8CRKL', 'B0CLGHHTS8', 'B0CLNGT26N', 'B0CLNGT2BM', 'B0CLNH39PT',
                'B0CLNHB2F9', 'B0CLNHDJFL', 'B0CLNHDVKK', 'B0CLNHHVR3', 'B0CLNJ2R3Q', 'B0CLNJ68DC',
                'B0CLNJ7CDK', 'B0CLNJ96B6', 'B0CLNJBTFD', 'B0CLNKD335', 'B0CLNKG96P', 'B0CLNKGMCQ', 'B0CLNKR4RY',
                'B0CLNKS66B', 'B0CLNLC8SR', 'B0CLNM7B6S', 'B0CLNMQKTB', 'B0CLNRKPJQ', 'B0CLP18LFB',
                'B0CLRN95KX', 'B0CLXMGMGH', 'B0CLXQ42P4', 'B0CLY3GR7L', 'B0CM36WKCR', 'B0CM9JL8CN', 'B0CM9JV8PN',
                'B0CM9KCB5B', 'B0CM9LBJT3', 'B0CMXNCV14', 'B0CMXNLZMZ', 'B0CMXPC4HJ', 'B0CMXR1C5K', 'B0CMXRB3Z3',
                'B0CN31YNVX', 'B0CN6JQ5PN', 'B0CNBZPJM4', 'B0CP3N4N94', 'B0CP3NDW7T', 'B0CP3P6669', 'B0CP3PBJJZ',
                'B0CP3PMY2T', 'B0CPLV68HY', 'B0CPNY3S8W', 'B0CPP2GZWG', 'B0CPP3P3MC', 'B0CPP7M51V', 'B0CPPCHZBM',
                'B0CPPVHNVC', 'B0CQ52RZXS', 'B0CQCBMYDC', 'B0CRTN9WKL', 'B0CS5HKGV9', 'B0CS5R8L6T', 'B0CS5X6DWS',
                'B0CS5Y95J2', 'B0CS65S17Q', 'B0CS6BPVP1', 'B0CT5SB7DC', 'B0CTTC177G', 'B0CV3NQ153', 'B0CV3NW1DG',
                'B0CV3P28GS', 'B0CVX81X7R', 'B0CX1GWHSZ', 'B0CX95QV2T', 'B0CX95WTL9', 'B0CX96KHWC',
                'B0CX96Q8L2', 'B0CX97L85H', 'B0CXHWBCVM', 'B0CXJ72SWH', 'B0CXLZ55YK', 'B0CXP9RDT7', 'B0CXSZ7F34',
                'B0CXSZG3SV', 'B0CY1ZS3W3', 'B0CY24W29N', 'B0CYLTRVYX', 'B0CZNMF3MD', 'B0CZNMYTZ1', 'B0CZNTGYWB',
                'B0CZNV47H7', 'B0D12RN4NJ', 'B0D12SRV4P', 'B0D1CGLBSR', 'B0D1KGVCFK', 'B0D1KN5JDB', 'B0D1KNVFM7',
                'B0D1Q4M6CZ', 'B0D2DG52LS', 'B0D2DH9B8Z', 'B0D2DHM6TS', 'B0D2DJ2S21', 'B0D2DJ7HC8', 'B0D2DJ97LK',
                'B0D2DJGLRN', 'B0D2DK5RY2', 'B0D2DLKNJS', 'B0D2GRTT87', 'B0D2GRYPGH', 'B0D2H5JM74', 'B0D2L5J1JH',
                'B0D2L5J2S2', 'B0D2QBD9B4', 'B0D2QC98VK', 'B0D2QC9TZW', 'B0D2QD7BYZ', 'B0D2QDGF31', 'B0D2VQLJB7',
                'B0D2VQM4Q8', 'B0D2XJ91JV', 'B0D2XJSR92', 'B0D2XKND4F', 'B0D3LHYR5H', 'B0D3RKDVWM', 'B0D3RLN4Q7',
                'B0D3RLP2YV', 'B0D49G6RWH', 'B0D4K6TNJ8', 'B0D4K7C6TL', 'B0D4M2MV79', 'B0D4M43SVN', 'B0D4M8RL3K',
                'B0D4TR1GH5', 'B0D5482P98', 'B0D54B1JXL', 'B0D5CPYZM4', 'B0D5HGKH7Z', 'B0D5QW2Y9L', 'B0D5QX4DCP',
                'B0D6R1SNKY', 'B0D6R36V1K', 'B0D73PR95N', 'B0D7BP1RDB', 'B0D7P9FQ24', 'B0D7P9L9CL', 'B0D7QBNPZP',
                'B0D7VNPWLK', 'B0D7VP38SM', 'B0D83GBTK3', 'B0D8BJC8F2', 'B0D8KX3ZQJ', 'B0D8KYKXJ9', 'B0D8KZ679K',
                'B0D9293QP9', 'B0DCNP8GNG', 'B0D5QVBPTL', 'B0D5QKY1KN', 'B0D5QKGCRF', 'B0D5R41NWS', 'B0D5R1C5ZW',
                'B0D1KMGQ2C', 'B0D1KMJ5X2', 'B0DC64GLQL', 'B0DCNP8GNG', 'B0DFCR889X', 'B0DFCQ8498', 'B0DFCPVGP2',
                'B0CLGYTNVV', 'B0CLGW9YWJ', 'B0DDCW6ZKB', 'B0DDCW2Y3Z', 'B0DDCYDGFH', 'B0DGWYVLT7', 'B0DGX1LGV7',
                'B0DGWZ961D', 'B0DGWZ2WLZ', 'B0DGWXNL1B', 'B0D1XMYWJW', 'B0DGWXDVDW', 'B0DJ79262R', 'B0D1XWLWDX',
                'B0DGWZGQ3C', 'B0DJ79QNMB', 'B0DGWXYJ4S', 'B0DGWZ4DXY', 'B0D5R41NWS', 'B0DL9J7VKQ', 'B0D5R1C5ZW',
                'B0C4TGWSFV', 'B0C4T3XZHC', 'B0D5Y1JJVN', 'B0DL5CX3CZ', 'B0DL58QGN1', 'B0CF52DMX7', 'B0DL55WM1N',
                'B0D5QW84QF', 'B0DFW9KMKK', 'B0DFW92ZMR', 'B0DRY7BRBL', 'B0DRY31QH3', 'B0DRY31RV7', 'B0DJ2SF7JR',
                'B0DJ2SF7JR', 'B0DP79LBNT', 'B0DP774P78', 'B0DNZ63YMR', 'B0DNZ9RWDW', 'B0DXBLRHJV', 'B0DXBR8WRB',
                'B0DXCQTG9F', 'B0DXCRPFVJ', 'B0DXCBNMMD', 'B0DXCBDN8X', 'B0DXCRJ8VW', 'B0DXCPWS2Q', 'B0DXBLHD62',
                'B0DXBTLLL9', 'B0DXBQR4LW', 'B0DYCXGX4T', 'B0DYD4PM4Y', 'B0DYJTP9YF', 'B0DYJWL7XQ',
                'B0DYJWFJJW', 'B0DYJWQNF4', 'B0DTTWPBKR', 'B0DN1SD2VJ', 'B0DN1RFVVZ', 'B0DN1Q4SN3', 'B0DN1SMBXX',
                'B0DM6F9Q4S', 'B0DM6CZCDV', 'B0DM6DMY24', 'B0DM6BT163', 'B0DM6D3D6N', 'B0DM66DHS5', 'B0DM6D7C1C',
                'B0DZCJ7B3Y', 'B0DZCLHJ76', 'B0DDD8QGKT', 'B0DDDP1HGC', 'B0DDD6Z374'
                ]


    # 有新的asin时打开，把新asin放入''中
    # asin_all = ['B0DDD8QGKT', 'B0DDDP1HGC', 'B0DDD6Z374']

    # 测试
    # asin_all = ['B0DRY31QH3', 'B0DRY31RV7']

    # AC
    # asin_all = ['B0CS6BPVP1','B0CS5Y95J2','B0CT5SB7DC','B0CS5HKGV9','B0CS5R8L6T','B0CS65S17Q',
    #             'B0CS5X6DWS','B0D4K6TNJ8','B0BGLCBWHZ',
    #             ]

    ### -------------------------------运行前改时间和path-------------------------------------- ###

    date_update = '2025-03-24'  # 更新时间
    path = "2025 WGE DI Booking Master Sheet 20250317.xlsx"
    path1 = "Inventory_Manufacturing_Retail_UnitedStates_Custom.xlsx"

    spotter_cookie = '_ga=GA1.1.597751433.1741071909; _ga_SGKG3G1R4Z=GS1.1.1741075780.2.0.1741075780.0.0.0; spotter_token=207723062079493415_038a46190bef46d39529c8ba5b5e29f2; _ga_RY8G5KNR0N=GS1.1.1742372328.6.1.1742372332.56.0.0; _ga_ZLNLY89RRN=GS1.1.1742370578.38.1.1742372450.49.0.0'

    spotter_token = '207723062079493415_038a46190bef46d39529c8ba5b5e29f2'

    amazon_cookie = 'ubid-main=133-7518868-8574240; _mkto_trk=id:365-EFI-026&token:_mch-amazon.com-6b005e991ebcc93c2e110b3e6723a607; AMCV_4A8581745834114C0A495E2B%40AdobeOrg=179643557%7CMCIDTS%7C20153%7CMCMID%7C88509906194640433110619087631772830210%7CMCAAMLH-1741757642%7C3%7CMCAAMB-1741757642%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1741160042s%7CNONE%7CMCAID%7CNONE%7CMCSYNCSOP%7C411-20160%7CvVersion%7C5.5.0; session-id=140-1943140-5655424; mbox=session#a5ea2119b5a74512ab5463abb79bf581#1741154845|PC#a5ea2119b5a74512ab5463abb79bf581.38_0#1804397785; s_nr=1741152984585-New; s_lv=1741152984585; sst-main=Sst1|PQHo-TXi7sxwvu5UCI22YVYBCU5trS9ldMrnN18ENNfvsDqd1zK_T9z67nOWu76eqHIqI6nRM69xCUf55pTDEvOpDa9syKihoBKeUutFbzBxGrz956yqQ6ksJyRkxzmQzzpIZ2VhwNbD9hIXlfB06H_poCZnNqFwzRs1y-MQTuZMAumcs5vloo9iGCNJOLwqs-5LqDr1Gdh5PUjh6Qfka-a6blK-LURsAj28IFknoHhDIzd06KDsGwPIWxHNADVpZfs96GFuLUve7q5ulVoEcJWKFKtlsTNuiGpcLotlsdY7Kh0; kndctr_7742037254C95E840A4C98A6_AdobeOrg_identity=CiY4ODEyOTkzMzUyNjE4OTE3NTA4MDU3OTk2NTE1MzA0NjEwMTkyOVIRCI_Gu6bWMhgBKgRKUE4zMAHwAY_Gu6bWMg==; AMCV_7742037254C95E840A4C98A6%40AdobeOrg=MCMID|88129933526189175080579965153046101929; __Host-mselc=H4sIAAAAAAAA/6tWSs5MUbJSSsytyjPUS0xOzi/NK9HLT85M0XM0MnDyMY7wMgp08vExUdJRKktHUlqWrmdmZGloZmioVAsArqk8DUUAAAA=; i18n-prefs=USD; lc-main=en_US; id_pkel=n1; id_pk=eyJuIjoiMSJ9; csm-hit=tb:EBB1A45SH02SG0QTR6W1+s-YFB1WB2V2Z9G35YKDE6N|1742782267113&t:1742782267113&adb:adblk_no; session-id-time=2373502360l; session-token="x6CvIOAj+8ir6rgjW97bpKVkGhTQTsxsLgFsXH4Ek06GNFsTigkilA8UxWJwsV0ruF5wCWnZ1afZyuPS6v8ZFJlKbSo/I0h7n33ajJYBgiHg6je9FMarz/4ABgMycqEaXva0NTuIp1pGGOdxRfrqXHyEL/Grzz3cHPy95wxkKkSa4zVSwtB5MhLm5dt/ChjwwYGQhyXYUTkLKpcntlrpUsBZpJtHA834iSeBDoH7zoBkWHgUOllqOKEXjTa9E/J9q8o4V6BcrtW/5YWXiRGArt8SbH1LOKF7KRHFKoOLsueYHRnzJhqxrZGlYbpAXbK2gOuOBzbrB6Q5aqtxC95F2wN3k+13qhhUiWPID9Hvfbmk2FVABEttxg=="; x-main="aWxSXdRPeMEaMn5A5EG6ores1JUaKpYMluNCvASMv@@BP5xE95lBCQcL0h4@ZbRz"; at-main=Atza|IwEBILNWv5HibPd01YfB2Y8u8JfJRqg5OBzSc5vxpmsxAZLi4d8DbEzYHRQYkyBBOQ_b3ouCTk5UbF6n_Q1BJR1XOVl49ejh91drZJDFwWz-53z1eKC1MT65e-sH-05CC9MEBVojiDTf7hlOipS8S93j6wq7flwkyVmPDY8QIkmUhFZ7YfD4ZX3WQ4UxLDi5XA8N_iKspqfuyJVdspEV_jX5QMjfwT2T52c6SlOGUhB7SroFarMMF4bRRuZg0FL2llydER4; sess-at-main="NHG18t6Ye14yVW2TazAsNR3cLEGs3E4vbokoB7MOOjQ="'

    ### ------------------------------------------------------------------------------------- ###

    # 设置http请求头
    headers_spotter = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://sevc.spotterio.com",
        "Referer": "https://sevc.spotterio.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Authentication-Token": spotter_token,
        "X-app": "sevc",
        "X-site-tenant": "US_AMZ",
        "X-spotter-i18n": "zh_Hans",
        "X-sso-version": "v3",
        "X-tenant-id": "US_default"
    }
    headers = {
        'accept': 'application/json',
        'accept-language': 'zh-CN,zh;q=0.9',
        'amz-ara-custom-context': '{"timezoneOffset":-480,"traceId":"2de52487-45d4-431b-884b-e424ce22d066","selectedVendorGroupIds":["6291611"],"cid":"A38NLTKOOLFG3Q"}',
        'anti-csrftoken-a2z': 'hE+4Azkl/Thz/FA2W2f/15DQk6xYQPPYcMOydhzhiBQRAAAAAGcM4g01MzExY2ZiYi1iOWRjLTQ5YjktOTA4ZC01ZWI4Nzk0ZWYxYWY=',
        'content-type': 'application/json',
        # 运行前改cookie，去亚马逊上找
        'cookie': amazon_cookie,
        'origin': 'https://vendorcentral.amazon.com',
        'priority': 'u=1, i',
        'referer': 'https://vendorcentral.amazon.com/retail-analytics/dashboard/inventory?submit=true',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    # 读取两个Excel数据
    df_asin_info = pd.read_excel(path,sheet_name='Grid-US')
    df_asin_info['Booking#'] = df_asin_info['Booking#'].str.strip()

    df_book_info = pd.read_excel(path,sheet_name='汇总-US')
    df_book_info['Booking#'] = df_book_info['Booking#'].str.strip()

    result_inner = pd.merge(df_asin_info, df_book_info[['Booking#', 'ETD']], on='Booking#', how='left')
    result_inner.fillna(0, inplace=True)
    result_inner = result_inner[result_inner['ETD'] != 0]


    # sevc库存数据

    # 海外仓数据
    SEVC_out_sea_inventory_1 = 0
    SEVC_out_sea_inventory_2 = 0
    SEVC_out_sea_inventory_3 = 0
    try:
        SEVC_out_sea_inventory_1 = out_sea_inventory(headers_spotter, 1)
    except Exception as e:
        print(e)
        while True:
            time.sleep(5)
            try:
                SEVC_out_sea_inventory_1 = out_sea_inventory(headers_spotter, 1)
                break
            except Exception:
                continue
    try:
        SEVC_out_sea_inventory_2 = out_sea_inventory(headers_spotter, 2)
    except Exception as e:
        print(e)
        while True:
            time.sleep(5)
            try:
                SEVC_out_sea_inventory_2 = out_sea_inventory(headers_spotter, 2)
                break
            except Exception:
                continue
    try:
        SEVC_out_sea_inventory_3 = out_sea_inventory(headers_spotter, 3)
    except Exception as e:
        print(e)
        while True:
            time.sleep(5)
            try:
                SEVC_out_sea_inventory_3 = out_sea_inventory(headers_spotter, 3)
                break
            except Exception:
                continue

    SEVC_out_sea_inventory = SEVC_out_sea_inventory_1 + SEVC_out_sea_inventory_2 + SEVC_out_sea_inventory_3
    print(SEVC_out_sea_inventory)


    # vc后台库存
    # 获取可售库存
    Open_Purchases = get_open_purchase(path1)
    Sellable_On_Hand_Units = get_amz_avaibletoSale(path1)


    # sevc 运输数据
    df_asin.fillna(0, inplace=True)  # 处理缺失值 转换为0

    link = get_api_info_amount_all_sevc().split('dashboard/')[1].split('#')[0]

    # 遍历每一个asin
    for asin in asin_all:

        data_part = []

        # 在途库存以及open purchase 调用 fetch_data_for_all_asins_and_months 函数获取亚马逊的库存和PO数据
        data_result = fetch_data_for_all_asins_and_months(headers, asin, result_inner)

        # 初始化变量
        saleAvailableTotal_all = 0  # 海外仓可售po
        # in_stock_all = 0  # 在库总件数
        frozen_stock_all = 0  # 冻结总件数

        open_purchases_quanity = 0  # open purchases
        Sellable_Units = 0  # 亚马逊可售
        # df_sale_units = 0  # 海外仓可售DF
        qty_di_amz_wait = 0

        # 从data_result中提取数据结果
        qty_outstanding_all_di = data_result[1]  # 亚马逊不包含接收中的那部分数量  在途和待发
        qty_open_purchase_all_di = data_result[2]
        qty_outstanding_all_do = data_result[3]
        qty_open_purchase_all_do = data_result[4]
        qty_outstanding_all_di_on_ship = data_result[5]
        qty_outstanding_all_di_received = data_result[6]


        # 提取catagory sku
        sku = '/'
        for index, row in df_asin.iterrows():
            if row[0] == asin:
                name = row[12]
                catagory = row[14]
                sku = row[8]
                break

        WaitDeliverNum_all = 0  # po订单占用
        availableTotal = 0
        saleAvailableTotal_all = 0
        over_age_num = 0

        # 提取海外仓库存数据
        for info in SEVC_out_sea_inventory:
            saleAvailableTotal = 0
            if asin == info.get('asin'):
                if info.get('availableNum'):
                    saleAvailableTotal = info.get('availableNum')
                saleAvailableTotal_all += saleAvailableTotal
                # 提取po订单占用
                sku = info.get('ssku')
                storageCode = info.get('storageCode')
                flag = 0

                try :
                    if get_WaitDeliverNum_all(sku,storageCode):  # 判断不为空
                        for info1 in get_WaitDeliverNum_all(sku,storageCode):
                            if info1.get('occupyTypeDesc') == "PO订单出库":
                                WaitDeliverNum_all += int(info1.get('totalSingleOccupy'))
                                flag += flag
                                if flag == 5:
                                    break
                except Exception:
                    if get_WaitDeliverNum_all(sku,storageCode):  # 判断不为空
                        for info1 in get_WaitDeliverNum_all(sku,storageCode):
                            if info1.get('occupyTypeDesc') == "PO订单出库":
                                WaitDeliverNum_all += int(info1.get('totalSingleOccupy'))
                                flag += flag
                                if flag == 5:
                                    break




        # 提取冻结库存数据
        # df_sale_units = 0  # 暂时置0
        # try:
        #     if df_inventory(asin,headers_spotter):
        #         df_inventory_result = df_inventory(asin,headers_spotter)
        #         for info in df_inventory_result:
        #             if asin==info.get('asin'):
        #                 freezeTotal = info.get('freezeTotal')
        #                 df_sale_units += freezeTotal
        # except Exception:
        #     try:
        #         if df_inventory(asin,headers_spotter):
        #             df_inventory_result = df_inventory(asin,headers_spotter)
        #             for info in df_inventory_result:
        #                 if asin==info.get('asin'):
        #                     freezeTotal = info.get('freezeTotal')
        #                     df_sale_units += freezeTotal
        #     except Exception:
        #         freezeTotal = 0
        #         df_sale_units = 0
        #         break

        # 提取亚马逊Open Purchase
        for info in Open_Purchases:
            if asin == info[0]:
                open_purchases_quanity = info[1]
                break


        # 提取亚马逊可售库存数据
        for info in Sellable_On_Hand_Units:
            if asin == info[0]:
                Sellable_Units = info[1]
                over_age_num = info[2]
                break

        try:
            result_approving = approving_ship_units(asin, headers_spotter)
            # print(result_approving)
        except Exception:
            flag = 1
            while True:
                time.sleep(3)
                if flag == 5:
                    break
                try:
                    result_approving = approving_ship_units(asin, headers_spotter)
                    break
                except Exception as e:
                    print(e)


        # 提取确认中的库存数据
        try:
            result_shipping = shipping_units(asin, headers_spotter)
            # print(result_shipping)
        except Exception:
            flag = 1
            while True:
                time.sleep(3)
                if flag == 5:
                    break
                try:
                    result_shipping = shipping_units(asin, headers_spotter)
                    break
                except Exception as e:
                    print(e)
        # print(get_api_info_amount_all_sevc())

        # print(link)

        # 提取运输中的库存数据
        shipping_do = 0  # 海运在途do
        if result_approving:
            for info in result_approving:
                ship_num = info.get('ssku')
                try:
                    result = approving_ship_units_result(link,ship_num)
                    # print(f'result:{result}')
                except Exception:
                    flag = 1
                    while True:
                        time.sleep(3)
                        if flag == 5:
                            break
                        try:
                            result = approving_ship_units_result(link,ship_num)
                            break
                        except Exception as e:
                            print(e)

            for info1 in result:
                shipping_do += int(info1[6])

        # 已下单未发货
        odered_waitingforship = 0
        for info in df_sheet:
            fields = info.get('fields')
            asin_odered = dict(fields).get('ASIN')[0].get('text')
            if asin_odered == asin:
                try:
                    odered_waitingforship = dict(fields).get('已下单未发货-AMZ')
                except:
                    odered_waitingforship = 0
                break


        inventory_all = int(
            int(Sellable_Units) + saleAvailableTotal_all + shipping_do + qty_outstanding_all_do + qty_outstanding_all_di_on_ship
            + qty_outstanding_all_di_received
        )


        #有新asin时打开，否则关闭
        data_part.append(asin)
        data_part.append(catagory)
        data_part.append(name)

        data_part.append(inventory_all)  # 总库存
        data_part.append(open_purchases_quanity)  # open purchases
        # 1.亚马逊可售
        data_part.append(Sellable_Units)
        # 2.亚马逊在途PO  di在途 + di接收中 + do在途
        data_part.append(int(qty_outstanding_all_di_on_ship + qty_outstanding_all_di_received + qty_outstanding_all_do))
        # 2.1亚马逊在途PO（di） = di在途 + di接收中
        data_part.append(int(qty_outstanding_all_di_on_ship + qty_outstanding_all_di_received))  # 在运输中的di包括接收中
        # 2.1.1亚马逊在途PO（di）接收中
        # data_part.append(qty_outstanding_all_di_received)
        # 2.2亚马逊在途PO（do）
        data_part.append(qty_outstanding_all_do)
        # 2.2.1海外仓占用PO
        data_part.append(WaitDeliverNum_all)
        # 3.海外仓可售PO
        data_part.append(saleAvailableTotal_all)
        # 4.海运在途DO
        data_part.append(shipping_do)
        # 5.亚马逊PO（di）待发
        data_part.append(int(qty_outstanding_all_di - qty_outstanding_all_di_on_ship))
        # 更新日期
        data_part.append(date_update)
        # sku
        data_part.append(sku)
        # 接收中
        data_part.append(qty_outstanding_all_di_received)
        # 1.1超期库存
        data_part.append(int(over_age_num))
        # 已下单未发货
        data_part.append(int(odered_waitingforship))

        print('------->')
        print(asin)
        print(data_part)
        print('------->')

        #有新asin时关闭
        # data_part.append(asin)
        # mysql_data_update(data_part)

        # 有新asin时打开，否则关闭
        mysql_input(data_part)
