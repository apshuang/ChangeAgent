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
# 在这里修改要测试的接口
# ============================================================================
if __name__ == "__main__":
    # 取消注释要测试的方法
    # test_get()  # 不带认证的GET请求（可能返回403）
    # test_post()  # 登录获取token
    # test_get_with_auth()  # 带认证的GET请求
    test_get_all_routes()  # 获取所有路线信息
