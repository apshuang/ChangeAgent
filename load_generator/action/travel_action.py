"""
旅行相关Action - 处理车次查询等旅行操作
"""
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

