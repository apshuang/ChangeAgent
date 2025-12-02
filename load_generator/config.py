"""
配置文件 - 定义TrainTicket系统的API端点和其他配置
按模块组织，便于维护和管理
"""
import os
from typing import Dict, List


# ============================================================================
# 基础配置
# ============================================================================

# TrainTicket系统的基础URL
BASE_URL = os.getenv("TRAINTICKET_BASE_URL", "http://10.10.1.98:32677")

# 请求超时时间（秒）
REQUEST_TIMEOUT = 30

# 默认请求头
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


# ============================================================================
# API端点配置
# ============================================================================

API_ENDPOINTS = {
    # 认证服务
    "auth": {
        "login": "/api/v1/users/login",
        "register": "/api/v1/auth",
    },
    # 旅行服务 - G/D列车
    "travel": {
        "trip_detail": "/api/v1/travelservice/trip_detail",
        "trips_left": "/api/v1/travelservice/trips/left",
    },
    # 旅行服务 - 其他列车
    "travel2": {
        "trip_detail": "/api/v1/travel2service/trip_detail",
        "trips_left": "/api/v1/travel2service/trips/left",
    },
    # 票务信息服务
    "ticketinfo": {
        "ticketinfo": "/api/v1/ticketinfoservice/ticketinfo",
        "station_id": "/api/v1/ticketinfoservice/ticketinfo/{name}",
    },
    # 预订服务 - G/D列车
    "preserve": {
        "preserve": "/api/v1/preserveservice/preserve",
    },
    # 预订服务 - 其他列车
    "preserve_other": {
        "preserve": "/api/v1/preserveotherservice/preserveOther",
    },
    # 内部支付服务
    "inside_payment": {
        "payment": "/api/v1/inside_pay_service/inside_payment",
        "account": "/api/v1/inside_pay_service/inside_payment/account",
        "topup": "/api/v1/inside_pay_service/inside_payment/{userId}/{money}",
    },
    # 订单服务
    "order": {
        "query": "/api/v1/orderservice/order/query",
        "get_by_id": "/api/v1/orderservice/order/{orderId}",
    },
    # 用户服务
    "user": {
        "get_by_id": "/api/v1/userservice/users/id/{userId}",
    },
    # 联系人服务
    "contact": {
        "get_by_id": "/api/v1/contactservice/contacts/{id}",
        "get_by_account": "/api/v1/contactservice/contacts/account/{accountId}",
    },
    # 路线服务
    "route": {
        "get_all": "/api/v1/routeservice/routes",
        "get_by_id": "/api/v1/routeservice/routes/{routeId}",
    },
}


# ============================================================================
# 认证模块配置
# ============================================================================

# 默认用户凭据（用于测试，实际应该从环境变量或配置文件读取）
DEFAULT_USERS = [
    {"username": "fdse_microservices", "password": "111111"},
    # 可以添加更多测试用户
]

# 管理员账号（用于注册等需要管理员权限的操作）
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "222222")


# ============================================================================
# 车站模块配置
# ============================================================================

# 车站列表（从实际API获取的车站信息）
DEFAULT_STATIONS = [
    "shijiazhuang",
    "jiaxingnan",
    "hangzhou",
    "nanjing",
    "taiyuan",
    "wuxi",
    "jinan",
    "shanghaihongqiao",
    "shanghai",
    "beijing",
    "xuzhou",
    "zhenjiang",
    "suzhou",
]

# 车站详细信息（包含ID和停留时间）
STATION_INFO = {
    "shijiazhuang": {"id": "15073e9a-7623-4f3d-b968-f412814fdbe4", "stayTime": 8},
    "jiaxingnan": {"id": "371d0ac8-56e3-42ee-9d85-3ad14d175b9c", "stayTime": 2},
    "hangzhou": {"id": "3c11a6c1-3d4e-430d-abd6-8e6e55dd451e", "stayTime": 9},
    "nanjing": {"id": "45b6fd3f-4079-4164-b4cf-f67d5b3da631", "stayTime": 8},
    "taiyuan": {"id": "49c6ba74-3385-45b8-a76c-dbf748e3c2be", "stayTime": 5},
    "wuxi": {"id": "72d1b915-17be-47c4-b350-2772bda3112a", "stayTime": 3},
    "jinan": {"id": "7f3bfc6d-f44a-405b-b30d-aafb8ced09f1", "stayTime": 5},
    "shanghaihongqiao": {"id": "883788fd-c26c-473d-956a-9c1f2cb70c96", "stayTime": 10},
    "shanghai": {"id": "8edb0ab9-81d4-46e6-ac9f-f4f97c23df19", "stayTime": 10},
    "beijing": {"id": "9a2d65c2-7623-470d-9383-c9a5b546dc10", "stayTime": 10},
    "xuzhou": {"id": "9b4ba7e1-dd33-4531-8010-d0b2c326ce9a", "stayTime": 7},
    "zhenjiang": {"id": "f24c486f-da1c-4138-92d4-8074e12c45a3", "stayTime": 2},
    "suzhou": {"id": "f7e4a226-08dc-4aa3-abe7-83c764980200", "stayTime": 3},
}


# ============================================================================
# 旅行模块配置
# ============================================================================

# 默认旅行日期
DEFAULT_TRAVEL_DATES = ["2024-12-25", "2024-12-26", "2024-12-27"]


# ============================================================================
# 路线模块配置
# ============================================================================

# 路线信息
# 格式: {起点站: {终点站: True/False}}
# 用于快速判断两个站点之间是否有路线

# 高铁/动车路线（travelservice - G/D列车）
ROUTES_HIGH_SPEED: Dict[str, Dict[str, bool]] = {
    "nanjing": {
        "shanghai": True,
        "suzhou": True,
        "wuxi": True,
        "zhenjiang": True,
    },
    "shanghai": {
        "suzhou": True,
    },
    "suzhou": {
        "shanghai": True,
    },
    "wuxi": {
        "shanghai": True,
        "suzhou": True,
    },
    "zhenjiang": {
        "shanghai": True,
        "suzhou": True,
        "wuxi": True,
    },
}

# 普通火车路线（travel2service - K/T/Z等列车）
ROUTES_NORMAL: Dict[str, Dict[str, bool]] = {
    "jiaxingnan": {
        "hangzhou": True,
    },
    "jinan": {
        "beijing": True,
    },
    "nanjing": {
        "beijing": True,
        "jinan": True,
        "shanghai": True,
        "shijiazhuang": True,
        "taiyuan": True,
        "xuzhou": True,
    },
    "shanghai": {
        "nanjing": True,
        "shijiazhuang": True,
        "taiyuan": True,
    },
    "shanghaihongqiao": {
        "hangzhou": True,
        "jiaxingnan": True,
    },
    "shijiazhuang": {
        "nanjing": True,
        "shanghai": True,
        "taiyuan": True,
    },
    "taiyuan": {
        "nanjing": True,
        "shanghai": True,
        "shijiazhuang": True,
    },
    "xuzhou": {
        "beijing": True,
        "jinan": True,
    },
}
