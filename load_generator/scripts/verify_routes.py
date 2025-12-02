"""
验证路线脚本
通过实际查询来验证哪些路线有高铁/动车，哪些有普通火车
然后生成config中的ROUTES_HIGH_SPEED和ROUTES_NORMAL配置
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://10.10.1.98:32677"

# 从config中导入车站列表（简化版，实际应该从config导入）
STATIONS = [
    "shijiazhuang", "jiaxingnan", "hangzhou", "nanjing", "taiyuan",
    "wuxi", "jinan", "shanghaihongqiao", "shanghai", "beijing",
    "xuzhou", "zhenjiang", "suzhou"
]

def get_all_routes():
    """获取所有路线信息"""
    endpoint = "/api/v1/routeservice/routes"
    url = f"{BASE_URL}{endpoint}"
    
    print(f"正在获取所有路线信息...")
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"❌ 获取路线失败，状态码: {response.status_code}")
        return None
    
    try:
        data = response.json()
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            routes = data.get("data", [])
            if isinstance(routes, list):
                return routes
    except Exception as e:
        print(f"❌ 解析路线数据失败: {e}")
        return None
    
    return None

def query_trips(start, end, date, service_type="high_speed"):
    """
    查询车次
    service_type: "high_speed" 或 "normal"
    """
    if service_type == "high_speed":
        endpoint = "/api/v1/travelservice/trips/left"
    else:
        endpoint = "/api/v1/travel2service/trips/left"
    
    url = f"{BASE_URL}{endpoint}"
    data = {
        "startPlace": start,
        "endPlace": end,
        "departureTime": date
    }
    
    try:
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list):
                return len(result) > 0
            elif isinstance(result, dict):
                trips = result.get("data", [])
                if isinstance(trips, list):
                    return len(trips) > 0
        return False
    except:
        return False

def extract_stations_from_route(route):
    """
    从路线数据中提取所有途径站点
    路线可能包含stations字段，是一个站点列表
    返回站点名称列表（按顺序）
    """
    stations = []
    
    # 尝试不同的字段名
    stations_data = route.get("stations") or route.get("stationList") or route.get("stationIds")
    
    if isinstance(stations_data, list):
        for station in stations_data:
            if isinstance(station, dict):
                # 尝试获取站点名称
                name = (station.get("name") or station.get("stationName") or 
                       station.get("station") or station.get("id"))
                if name:
                    stations.append(str(name))
            elif isinstance(station, str):
                stations.append(station)
    
    # 如果没有stations字段，尝试从startStation和endStation构建
    if not stations:
        start = route.get("startStationName") or route.get("startStation") or route.get("startStationId")
        end = route.get("endStationName") or route.get("endStation") or route.get("endStationId")
        if start and end:
            stations = [start, end]
    
    return stations

def generate_station_pairs(stations):
    """
    从站点列表中生成所有可能的站点对
    例如：[A, B, C, D] -> [(A,B), (A,C), (A,D), (B,C), (B,D), (C,D)]
    只生成前面的站点到后面站点的对（单向）
    """
    pairs = set()
    for i in range(len(stations)):
        for j in range(i + 1, len(stations)):
            pairs.add((stations[i], stations[j]))
    return pairs

def verify_routes():
    """验证路线"""
    print("=" * 60)
    print("路线验证工具")
    print("=" * 60)
    
    # 获取所有路线
    routes = get_all_routes()
    if not routes:
        print("\n❌ 无法获取路线数据")
        return
    
    print(f"\n获取到 {len(routes)} 条路线")
    
    # 从所有路线中提取站点对
    all_station_pairs = set()
    
    print("\n正在分析路线中的途径站点...")
    for i, route in enumerate(routes):
        if isinstance(route, dict):
            stations = extract_stations_from_route(route)
            if len(stations) >= 2:
                pairs = generate_station_pairs(stations)
                all_station_pairs.update(pairs)
                print(f"  路线 {i+1}: {len(stations)} 个站点 -> {len(pairs)} 个站点对")
                if len(stations) <= 5:  # 只显示短路线
                    print(f"    站点: {' -> '.join(stations)}")
    
    print(f"\n总共提取到 {len(all_station_pairs)} 个可能的站点对")
    
    # 使用未来日期进行查询
    future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    print(f"\n使用日期: {future_date} 进行验证")
    print("注意：验证过程可能需要较长时间...\n")
    
    routes_high_speed = {}
    routes_normal = {}
    
    # 验证每个站点对
    total = len(all_station_pairs)
    current = 0
    
    for start, end in sorted(all_station_pairs):
        current += 1
        print(f"[{current}/{total}] 验证: {start} -> {end}", end=" ... ")
        
        # 查询高铁/动车
        has_high_speed = query_trips(start, end, future_date, "high_speed")
        # 查询普通火车
        has_normal = query_trips(start, end, future_date, "normal")
        
        if has_high_speed:
            if start not in routes_high_speed:
                routes_high_speed[start] = {}
            routes_high_speed[start][end] = True
            print("✓ 高铁", end="")
        
        if has_normal:
            if start not in routes_normal:
                routes_normal[start] = {}
            routes_normal[start][end] = True
            print(" ✓ 普通", end="")
        
        if not has_high_speed and not has_normal:
            print("✗ 无车次", end="")
        
        print()
    
    # 生成配置代码
    print("\n" + "=" * 60)
    print("生成的配置代码：")
    print("=" * 60)
    
    config_code = "\n# 路线信息（自动生成）\n"
    config_code += "# 格式: {起点站: {终点站: True}}\n"
    config_code += "# 高铁/动车路线（travelservice - G/D列车）\n"
    config_code += "ROUTES_HIGH_SPEED: dict[str, dict[str, bool]] = {\n"
    
    if routes_high_speed:
        for start, ends in sorted(routes_high_speed.items()):
            config_code += f'    "{start}": {{\n'
            for end in sorted(ends.keys()):
                config_code += f'        "{end}": True,\n'
            config_code += "    },\n"
    else:
        config_code += "    # 未找到高铁/动车路线\n"
    
    config_code += "}\n\n"
    config_code += "# 普通火车路线（travel2service - K/T/Z等列车）\n"
    config_code += "ROUTES_NORMAL: dict[str, dict[str, bool]] = {\n"
    
    if routes_normal:
        for start, ends in sorted(routes_normal.items()):
            config_code += f'    "{start}": {{\n'
            for end in sorted(ends.keys()):
                config_code += f'        "{end}": True,\n'
            config_code += "    },\n"
    else:
        config_code += "    # 未找到普通火车路线\n"
    
    config_code += "}\n"
    
    print(config_code)
    
    print("\n统计信息：")
    print(f"  高铁/动车路线: {sum(len(ends) for ends in routes_high_speed.values())} 条")
    print(f"  普通火车路线: {sum(len(ends) for ends in routes_normal.values())} 条")
    
    # 保存到文件
    output_file = "routes_config_output.py"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(config_code)
    print(f"\n配置已保存到: {output_file}")

if __name__ == "__main__":
    verify_routes()

