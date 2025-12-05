"""
API接口测试脚本 - 简洁版
"""
import requests
import json

BASE_URL = "http://10.10.1.98:32677"

# ============================================================================
# 通用响应处理函数
# ============================================================================
def print_response(response):
    """智能打印响应内容，自动适配不同类型"""
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
    
    content_type = response.headers.get('Content-Type', '').lower()
    
    # 尝试解析JSON
    if 'application/json' in content_type:
        try:
            data = response.json()
            print("Response (JSON):")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except:
            print("Response (Text):")
            print(response.text)
    # 处理文本类型
    elif 'text/' in content_type:
        print("Response (Text):")
        print(response.text)
    # 处理HTML
    elif 'text/html' in content_type:
        print("Response (HTML):")
        print(response.text[:500])  # 只打印前500字符
    # 处理二进制
    elif 'image/' in content_type or 'application/octet-stream' in content_type:
        print(f"Response (Binary): {len(response.content)} bytes")
    # 其他情况，尝试JSON，失败则显示文本
    else:
        try:
            data = response.json()
            print("Response (JSON):")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except:
            if response.text:
                print("Response (Text):")
                print(response.text)
            else:
                print(f"Response (Empty or Binary): {len(response.content)} bytes")

# ============================================================================
# GET请求示例
# ============================================================================
def test_get():
    endpoint = "/api/v1/users"
    url = f"{BASE_URL}{endpoint}"
    
    print(f"GET {url}")
    response = requests.get(url)
    print_response(response)

# ============================================================================
# POST请求示例
# ============================================================================
def test_post():
    endpoint = "/api/v1/users/login"
    url = f"{BASE_URL}{endpoint}"
    data = {
        "username": "fdse_microservice",
        "password": "111111"
    }
    
    print(f"POST {url}")
    print(f"Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
    response = requests.post(url, json=data)
    print_response(response)
    
    # 如果登录成功，提取token
    if response.status_code == 200:
        try:
            result = response.json()
            token = result.get("data", {}).get("token")
            if token:
                print(f"\n✅ Token: {token[:50]}...")
                return token
        except:
            pass
    return None

# ============================================================================
# 带认证的GET请求示例
# ============================================================================
def test_get_with_auth():
    # 先登录获取token
    token = None
    endpoint = "/api/v1/users/login"
    url = f"{BASE_URL}{endpoint}"
    data = {
        "username": "admin",
        "password": "222222"
    }
    
    print(f"POST {url}")
    print(f"Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
    response = requests.post(url, json=data)
    print_response(response)
    
    # 如果登录成功，提取token
    if response.status_code == 200:
        try:
            result = response.json()
            token = result.get("data", {}).get("token")
            if token:
                print(f"\n✅ Token: {token[:50]}...")
        except:
            pass

    if not token:
        print("❌ 登录失败，无法获取token")
        return
    
    # # 第二步：注册用户
    # endpoint = "/api/v1/adminuserservice/users"
    # url = f"{BASE_URL}{endpoint}"
    # headers = {"Authorization": f"Bearer {token}"}

    # data = {
    #     "documentType": "1",
    #     "documentNum": "123456789012345678",
    #     "email": "test@test.com",
    #     "gender": "1",
    #     "userName": "test",
    #     "password": "111111"
    # }
    # print(f"\nPOST {url} (注册用户)")
    # print(f"Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
    # response = requests.post(url, json=data, headers=headers)
    # print_response(response)
    
    # # 从注册响应中提取userId
    # user_id = None
    # if response.status_code == 200:
    #     try:
    #         result = response.json()
    #         if result.get("status") == 1:
    #             user_id = result.get("data", {}).get("userId")
    #             if user_id:
    #                 print(f"\n✅ 注册成功，用户ID: {user_id}")
    #     except:
    #         pass
    
    # if not user_id:
    #     print("❌ 注册失败，无法获取用户ID，跳过删除操作")
    #     return
    
    user_id = "ed5c5491-c4e1-431d-bc14-cff9e04c9d75"
    # 第三步：删除用户
    endpoint = f"/api/v1/adminuserservice/users/{user_id}"
    url = f"{BASE_URL}{endpoint}"
    print(f"\nDELETE {url} (删除用户)")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(url, headers=headers)
    print_response(response)
    
    if response.status_code == 200:
        print("\n✅ 删除用户成功")
    else:
        print(f"\n❌ 删除用户失败，状态码: {response.status_code}")

# ============================================================================
# 获取所有路线信息
# ============================================================================
def test_get_all_routes():
    """获取所有路线信息（不需要登录）"""
    endpoint = "/api/v1/routeservice/routes"
    url = f"{BASE_URL}{endpoint}"
    
    print(f"GET {url}")
    print("获取所有路线信息...")
    response = requests.get(url)
    print_response(response)
    
    # 如果成功，尝试解析并显示路线数量
    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, list):
                print(f"\n✅ 成功获取 {len(data)} 条路线信息")
            elif isinstance(data, dict):
                # 可能是Response包装格式
                routes = data.get("data", [])
                if isinstance(routes, list):
                    print(f"\n✅ 成功获取 {len(routes)} 条路线信息")
        except:
            pass

# ============================================================================
# 保险服务测试
# ============================================================================
def get_user_token(username="fdse_microservice", password="111111"):
    """获取普通用户token"""
    endpoint = "/api/v1/users/login"
    url = f"{BASE_URL}{endpoint}"
    data = {
        "username": username,
        "password": password
    }
    
    print(f"POST {url} (登录获取token)")
    print(f"Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        try:
            result = response.json()
            token = result.get("data", {}).get("token")
            if token:
                print(f"✅ 登录成功，获取到token")
                return token
        except:
            pass
    
    print("❌ 登录失败，无法获取token")
    return None

def test_get_all_assurances():
    """获取所有保险信息（需要登录）"""
    # 先登录获取token
    token = get_user_token()
    if not token:
        return
    
    endpoint = "/api/v1/assuranceservice/assurances/assurance"
    url = f"{BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\nGET {url} (获取所有保险信息)")
    response = requests.get(url, headers=headers)
    print_response(response)
    
    # 如果成功，尝试解析并显示保险数量
    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, list):
                print(f"\n✅ 成功获取 {len(data)} 条保险信息")
            elif isinstance(data, dict):
                # 可能是Response包装格式
                assurances = data.get("data", [])
                if isinstance(assurances, list):
                    print(f"\n✅ 成功获取 {len(assurances)} 条保险信息")
        except:
            pass

def test_get_assurance_types():
    """获取保险类型（需要登录）"""
    # 先登录获取token
    token = get_user_token()
    if not token:
        return
    
    endpoint = "/api/v1/assuranceservice/assurances/types"
    url = f"{BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\nGET {url} (获取保险类型)")
    response = requests.get(url, headers=headers)
    print_response(response)
    
    # 如果成功，尝试解析并显示保险类型数量
    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, list):
                print(f"\n✅ 成功获取 {len(data)} 种保险类型")
            elif isinstance(data, dict):
                # 可能是Response包装格式
                types = data.get("data", [])
                if isinstance(types, list):
                    print(f"\n✅ 成功获取 {len(types)} 种保险类型")
        except:
            pass

# ============================================================================
# 食物服务测试
# ============================================================================
def test_get_all_foods(date="2024-12-25", start_station="shanghai", end_station="suzhou", trip_id="D1345"):
    """
    获取所有食物信息
    
    Args:
        date: 日期，格式：YYYY-MM-DD
        start_station: 起点站名称
        end_station: 终点站名称
        trip_id: 车次ID（例如：G1234, D5678等）
    """
    endpoint = f"/api/v1/foodservice/foods/{date}/{start_station}/{end_station}/{trip_id}"
    url = f"{BASE_URL}{endpoint}"
    
    print(f"GET {url}")
    print(f"参数: 日期={date}, 起点={start_station}, 终点={end_station}, 车次={trip_id}")
    response = requests.get(url)
    print_response(response)
    
    # 如果成功，尝试解析并显示食物数量
    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, list):
                print(f"\n✅ 成功获取 {len(data)} 条食物信息")
            elif isinstance(data, dict):
                # 可能是Response包装格式
                foods = data.get("data", [])
                if isinstance(foods, list):
                    print(f"\n✅ 成功获取 {len(foods)} 条食物信息")
        except:
            pass

# ============================================================================
# 联系人服务测试
# ============================================================================
def test_get_contacts_by_account(account_id="4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f"):
    """
    根据账户ID获取所有联系人（需要登录）
    
    Args:
        account_id: 账户ID（UUID格式）
    """
    # 先登录获取token
    token = get_user_token()
    if not token:
        return
    
    endpoint = f"/api/v1/contactservice/contacts/account/{account_id}"
    url = f"{BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\nGET {url} (根据账户ID获取联系人)")
    print(f"账户ID: {account_id}")
    response = requests.get(url, headers=headers)
    print_response(response)
    
    # 如果成功，尝试解析并显示联系人数量
    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, list):
                print(f"\n✅ 成功获取 {len(data)} 个联系人")
                if len(data) > 0:
                    print("\n联系人列表：")
                    for i, contact in enumerate(data, 1):
                        contact_id = contact.get("id") or contact.get("contactsId")
                        name = contact.get("name") or contact.get("contactName")
                        print(f"  {i}. ID: {contact_id}, 姓名: {name}")
            elif isinstance(data, dict):
                # 可能是Response包装格式
                contacts = data.get("data", [])
                if isinstance(contacts, list):
                    print(f"\n✅ 成功获取 {len(contacts)} 个联系人")
                    if len(contacts) > 0:
                        print("\n联系人列表：")
                        for i, contact in enumerate(contacts, 1):
                            contact_id = contact.get("id") or contact.get("contactsId")
                            name = contact.get("name") or contact.get("contactName")
                            print(f"  {i}. ID: {contact_id}, 姓名: {name}")
        except:
            pass

# ============================================================================
# 预订服务测试
# ============================================================================
def test_preserve_ticket():
    """
    预订车票（preserve-service）
    这是一个复杂的接口，需要多个参数，包括车次信息、联系人、座位类型等
    """
    # 先登录获取token和用户信息
    token = get_user_token()
    if not token:
        return
    
    # 获取用户ID（accountId）
    # 通过登录接口获取，或者从用户信息中获取
    # 这里先尝试从登录响应中获取，如果没有则使用默认值
    account_id = None
    login_response = requests.post(
        f"{BASE_URL}/api/v1/users/login",
        json={"username": "fdse_microservice", "password": "111111"}
    )
    if login_response.status_code == 200:
        login_data = login_response.json()
        if isinstance(login_data, dict) and login_data.get("status") == 1:
            account_id = login_data.get("data", {}).get("userId")
    
    if not account_id:
        print("⚠️ 无法获取accountId，使用默认值")
        account_id = "4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f"
    else:
        print(f"✅ 获取到accountId: {account_id}")
    
    # 获取联系人ID（contactsId）
    contacts_id = None
    if account_id:
        contacts_endpoint = f"/api/v1/contactservice/contacts/account/{account_id}"
        contacts_response = requests.get(
            f"{BASE_URL}{contacts_endpoint}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if contacts_response.status_code == 200:
            contacts_data = contacts_response.json()
            if isinstance(contacts_data, dict) and contacts_data.get("status") == 1:
                contacts_list = contacts_data.get("data", [])
                if isinstance(contacts_list, list) and len(contacts_list) > 0:
                    contacts_id = contacts_list[0].get("id")
                    print(f"✅ 获取到contactsId: {contacts_id} (联系人: {contacts_list[0].get('name')})")
    
    if not contacts_id:
        print("⚠️ 无法获取contactsId，使用默认值")
        contacts_id = "82a0e480-13ef-48fd-b4d8-0d05bf48a5c0"
    
    # 构建预订请求
    endpoint = "/api/v1/preserveservice/preserve"
    url = f"{BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {token}"}
    
    # 根据实际抓包的payload结构
    data = {
        "accountId": account_id,  # 账户ID（UUID格式）
        "contactsId": contacts_id,  # 联系人ID（UUID格式）
        "tripId": "D1345",  # 车次ID（字符串格式，例如：G1234, D1345等）
        "seatType": "2",  # 座位类型（字符串格式）："1"-经济座，"2"-舒适座
        "date": "2025-12-05",  # 出发日期，格式：YYYY-MM-DD
        "from": "shanghai",  # 起点站名称
        "to": "suzhou",  # 终点站名称
        "assurance": "1",  # 保险类型索引（字符串格式），"0"表示不购买保险
        "foodType": 2,  # 食物类型（数字格式），0表示不订购食物
        "stationName": "suzhou",  # 站点名称（用于食物配送）
        "storeName": "Roman Holiday",  # 商店名称（用于食物配送）
        "foodName": "Soup",  # 食物名称
        "foodPrice": 3.7  # 食物价格
    }
    
    print(f"\nPOST {url} (预订车票)")
    print(f"Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
    response = requests.post(url, json=data, headers=headers)
    print_response(response)
    
    # 如果成功，尝试解析响应
    if response.status_code == 200:
        try:
            result = response.json()
            if isinstance(result, dict):
                if result.get("status") == 1:
                    print("\n✅ 预订成功")
                    data_obj = result.get("data", {})
                    if isinstance(data_obj, dict):
                        order_id = data_obj.get("id") or data_obj.get("orderId")
                    elif isinstance(data_obj, str):
                        order_id = data_obj
                    else:
                        order_id = result.get("id") or result.get("orderId")
                    if order_id:
                        print(f"订单ID: {order_id}")
                else:
                    print(f"\n❌ 预订失败: {result.get('msg', '未知错误')}")
        except Exception as e:
            print(f"\n⚠️ 解析响应时出错: {e}")

def test_preserve_other_ticket():
    """
    预订普通火车车票（preserve-other-service）
    这是一个复杂的接口，需要多个参数，包括车次信息、联系人、座位类型等
    用于预订非G/D列车的普通火车（K/T/Z等）
    """
    # 先登录获取token和用户信息
    token = get_user_token()
    if not token:
        return
    
    # 获取用户ID（accountId）
    account_id = None
    login_response = requests.post(
        f"{BASE_URL}/api/v1/users/login",
        json={"username": "fdse_microservice", "password": "111111"}
    )
    if login_response.status_code == 200:
        login_data = login_response.json()
        if isinstance(login_data, dict) and login_data.get("status") == 1:
            account_id = login_data.get("data", {}).get("userId")
    
    if not account_id:
        print("⚠️ 无法获取accountId，使用默认值")
        account_id = "4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f"
    else:
        print(f"✅ 获取到accountId: {account_id}")
    
    # 获取联系人ID（contactsId）
    contacts_id = None
    if account_id:
        contacts_endpoint = f"/api/v1/contactservice/contacts/account/{account_id}"
        contacts_response = requests.get(
            f"{BASE_URL}{contacts_endpoint}",
            headers={"Authorization": f"Bearer {token}"}
        )
        if contacts_response.status_code == 200:
            contacts_data = contacts_response.json()
            if isinstance(contacts_data, dict) and contacts_data.get("status") == 1:
                contacts_list = contacts_data.get("data", [])
                if isinstance(contacts_list, list) and len(contacts_list) > 0:
                    contacts_id = contacts_list[0].get("id")
                    print(f"✅ 获取到contactsId: {contacts_id} (联系人: {contacts_list[0].get('name')})")
    
    if not contacts_id:
        print("⚠️ 无法获取contactsId，使用默认值")
        contacts_id = "82a0e480-13ef-48fd-b4d8-0d05bf48a5c0"
    
    # 构建预订请求
    endpoint = "/api/v1/preserveotherservice/preserveOther"
    url = f"{BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {token}"}
    
    # 根据实际抓包的payload结构（普通火车）
    data = {
        "accountId": account_id,  # 账户ID（UUID格式）
        "contactsId": contacts_id,  # 联系人ID（UUID格式）
        "tripId": "Z1235",  # 车次ID（字符串格式，例如：K1234, T5678, Z1235等）
        "seatType": "2",  # 座位类型（字符串格式）："1"-舒适座，"2"-经济座
        "date": "2025-12-05",  # 出发日期，格式：YYYY-MM-DD
        "from": "xuzhou",  # 起点站名称
        "to": "beijing",  # 终点站名称
        "assurance": "1",  # 保险类型索引（字符串格式），"0"表示不购买保险
        "foodType": 1,  # 食物类型（数字格式），0表示不订购食物
        "foodName": "Bone Soup",  # 食物名称
        "foodPrice": 2.5,  # 食物价格
        "stationName": "",  # 站点名称（用于食物配送），可以为空
        "storeName": ""  # 商店名称（用于食物配送），可以为空
    }
    
    print(f"\nPOST {url} (预订普通火车车票)")
    print(f"Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
    response = requests.post(url, json=data, headers=headers)
    print_response(response)
    
    # 如果成功，尝试解析响应
    if response.status_code == 200:
        try:
            result = response.json()
            if isinstance(result, dict):
                if result.get("status") == 1:
                    print("\n✅ 预订成功")
                    data_obj = result.get("data", {})
                    if isinstance(data_obj, dict):
                        order_id = data_obj.get("id") or data_obj.get("orderId")
                    elif isinstance(data_obj, str):
                        order_id = data_obj
                    else:
                        order_id = result.get("id") or result.get("orderId")
                    if order_id:
                        print(f"订单ID: {order_id}")
                else:
                    print(f"\n❌ 预订失败: {result.get('msg', '未知错误')}")
        except Exception as e:
            print(f"\n⚠️ 解析响应时出错: {e}")

# ============================================================================
# 在这里修改要测试的接口
# ============================================================================
if __name__ == "__main__":
    # 取消注释要测试的方法
    # test_get()  # 不带认证的GET请求（可能返回403）
    # test_post()  # 登录获取token
    # test_get_with_auth()  # 带认证的GET请求
    # test_get_all_routes()  # 获取所有路线信息
    # test_get_all_assurances()  # 获取所有保险信息
    # test_get_assurance_types()  # 获取保险类型
    # test_get_all_foods()  # 获取所有食物信息
    # test_get_contacts_by_account()  # 根据账户ID获取联系人
    # test_preserve_ticket()  # 预订动车车票
    test_preserve_other_ticket()  # 预订普通火车车票
