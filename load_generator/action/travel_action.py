"""
旅行相关Action - 处理车次查询等旅行操作
"""
from typing import Any
from .base_action import BaseAction


class TravelAction(BaseAction):
    """旅行相关的API操作"""
    
    def query_trips_left(self, start_place: str, end_place: str, departure_time: str) -> list[dict[str, object]]:
        """
        查询高铁/动车剩余车票
        
        Args:
            start_place: 起点站名称
            end_place: 终点站名称
            departure_time: 出发日期
        
        Returns:
            车次列表，如果失败则返回空列表
            格式: [{"tripId": {...}, "trainTypeName": "...", "economyClass": 50, ...}, ...]
        """
        data = {
            "startPlace": start_place,
            "endPlace": end_place,
            "departureTime": departure_time
        }
        
        result = self._post("/api/v1/travelservice/trips/left", data)
        
        # 如果参数为空，接口直接返回空列表 []
        if isinstance(result, list):
            return result
        
        # 如果返回的是Response包装的格式
        if isinstance(result, dict):
            # 检查是否是Response格式
            if "status" in result and "data" in result:
                data_list = result.get("data")
                if isinstance(data_list, list):
                    return data_list
            # 如果不是Response格式，可能是直接返回的列表（在某些情况下）
            elif isinstance(result, list):
                return result
        
        return []
    
    def query_trips_left_normal(self, start_place: str, end_place: str, departure_time: str) -> list[dict[str, object]]:
        """
        查询普通火车剩余车票
        
        Args:
            start_place: 起点站名称
            end_place: 终点站名称
            departure_time: 出发日期
        
        Returns:
            车次列表，如果失败则返回空列表
            格式: [{"tripId": {...}, "trainTypeName": "...", "economyClass": 50, ...}, ...]
        """
        data = {
            "startPlace": start_place,
            "endPlace": end_place,
            "departureTime": departure_time
        }
        
        result = self._post("/api/v1/travel2service/trips/left", data)
        
        # 如果参数为空，接口直接返回空列表 []
        if isinstance(result, list):
            return result
        
        # 如果返回的是Response包装的格式
        if isinstance(result, dict):
            # 检查是否是Response格式
            if "status" in result and "data" in result:
                data_list = result.get("data")
                if isinstance(data_list, list):
                    return data_list
            # 如果不是Response格式，可能是直接返回的列表（在某些情况下）
            elif isinstance(result, list):
                return result
        
        return []
    
    def get_assurance_types(self, token: str) -> list[dict[str, object]]:
        """
        获取保险类型
        
        Args:
            token: 认证token（需要先登录获取）
        
        Returns:
            保险类型列表，如果失败则返回空列表
            格式: [{"index": 1, "name": "Traffic Accident Assurance", "price": 3.0}, ...]
        """
        headers = {"Authorization": f"Bearer {token}"}
        
        result = self._get("/api/v1/assuranceservice/assurances/types", headers=headers)
        
        # 如果返回的是Response包装的格式
        if isinstance(result, dict):
            # 检查是否是Response格式
            if "status" in result and "data" in result:
                if result.get("status") == 1:
                    data_list = result.get("data")
                    if isinstance(data_list, list):
                        return data_list
        # 如果直接返回列表
        elif isinstance(result, list):
            return result
        
        return []
    
    def get_all_foods(self, date: str, start_station: str, end_station: str, trip_id: str) -> dict[str, object]:
        """
        获取所有食物信息
        
        Args:
            date: 日期，格式：YYYY-MM-DD
            start_station: 起点站名称
            end_station: 终点站名称
            trip_id: 车次ID
        
        Returns:
            食物数据对象，如果失败则返回空字典
            格式: {"trainFoodList": [...], "foodStoreListMap": {...}}
        """
        endpoint = f"/api/v1/foodservice/foods/{date}/{start_station}/{end_station}/{trip_id}"
        
        result = self._get(endpoint)
        
        # 如果返回的是Response包装的格式
        if isinstance(result, dict):
            # 检查是否是Response格式
            if "status" in result and "data" in result:
                if result.get("status") == 1:
                    data_obj = result.get("data")
                    if isinstance(data_obj, dict):
                        return data_obj
        
        return {}
    
    def preserve_ticket(
        self,
        account_id: str,
        contacts_id: str,
        trip_id: str,
        seat_type: str,
        date: str,
        from_station: str,
        to_station: str,
        assurance: str,
        token: str,
        food_type: int = 0,
        station_name: str | None = None,
        store_name: str | None = None,
        food_name: str | None = None,
        food_price: float | None = None
    ) -> dict[str, object]:
        """
        预订动车车票
        
        Args:
            account_id: 账户ID（UUID格式）
            contacts_id: 联系人ID（UUID格式）
            trip_id: 车次ID（字符串格式，例如：G1234, D1345等）
            seat_type: 座位类型，"1"表示舒适座，"2"表示经济座
            date: 出发日期，格式：YYYY-MM-DD
            from_station: 起点站名称
            to_station: 终点站名称
            assurance: 保险类型索引，"0"表示不购买保险，其它索引都是对应的保险号
            token: 认证token（需要先通过login方法获取）
            food_type: 食物类型，0表示不订购食物，其它索引都是对应的食物类型，默认为0
            station_name: 站点名称（用于食物配送）
            store_name: 商店名称（用于食物配送）
            food_name: 食物名称
            food_price: 食物价格
            
        Returns:
            预订响应数据，如果失败则返回空字典或错误信息
            格式: {"status": 1, "msg": "Success.", "data": "Success"}
            失败时: {"status": 0, "msg": "Error message", "data": null} 或 {}
        """
        data: dict[str, Any] = {
            "accountId": account_id,
            "contactsId": contacts_id,
            "tripId": trip_id,
            "seatType": seat_type,
            "date": date,
            "from": from_station,
            "to": to_station,
            "assurance": assurance
        }
        
        # 如果订购食物，添加食物相关参数
        if food_type != 0:
            data["foodType"] = food_type
            if station_name:
                data["stationName"] = station_name
            if store_name:
                data["storeName"] = store_name
            if food_name:
                data["foodName"] = food_name
            if food_price is not None:
                data["foodPrice"] = food_price
        
        headers = {"Authorization": f"Bearer {token}"}
        
        result = self._post("/api/v1/preserveservice/preserve", data, headers=headers)
        
        # 预订接口返回格式: {"status": 1, "msg": "Success.", "data": "Success"}
        if isinstance(result, dict):
            return result
        return {}
    
    def preserve_other_ticket(
        self,
        account_id: str,
        contacts_id: str,
        trip_id: str,
        seat_type: str,
        date: str,
        from_station: str,
        to_station: str,
        assurance: str,
        token: str,
        food_type: int = 0,
        food_name: str | None = None,
        food_price: float | None = None,
        station_name: str | None = None,
        store_name: str | None = None
    ) -> dict[str, object]:
        """
        预订普通火车车票
        
        Args:
            account_id: 账户ID（UUID格式）
            contacts_id: 联系人ID（UUID格式）
            trip_id: 车次ID（字符串格式，例如：K1234, T5678, Z1235等）
            seat_type: 座位类型，"1"表示舒适座，"2"表示经济座
            date: 出发日期，格式：YYYY-MM-DD
            from_station: 起点站名称
            to_station: 终点站名称
            assurance: 保险类型索引，"0"表示不购买保险，其它索引都是对应的保险号
            token: 认证token（需要先通过login方法获取）
            food_type: 食物类型，0表示不订购食物，其它索引都是对应的食物类型，默认为0
            food_name: 食物名称
            food_price: 食物价格
            station_name: 站点名称（用于食物配送），可以为空字符串
            store_name: 商店名称（用于食物配送），可以为空字符串
            
        Returns:
            预订响应数据，如果失败则返回空字典或错误信息
            格式: {"status": 1, "msg": "Success.", "data": "Success"}
            失败时: {"status": 0, "msg": "Error message", "data": null} 或 {}
        """
        data: dict[str, Any] = {
            "accountId": account_id,
            "contactsId": contacts_id,
            "tripId": trip_id,
            "seatType": seat_type,
            "date": date,
            "from": from_station,
            "to": to_station,
            "assurance": assurance
        }
        
        # 如果订购食物，添加食物相关参数
        if food_type != 0:
            data["foodType"] = food_type
            if food_name:
                data["foodName"] = food_name
            if food_price is not None:
                data["foodPrice"] = food_price
            # stationName和storeName可以为空字符串
            data["stationName"] = station_name if station_name else ""
            data["storeName"] = store_name if store_name else ""
        
        headers = {"Authorization": f"Bearer {token}"}
        
        result = self._post("/api/v1/preserveotherservice/preserveOther", data, headers=headers)
        
        # 预订接口返回格式: {"status": 1, "msg": "Success.", "data": "Success"}
        if isinstance(result, dict):
            return result
        return {}

