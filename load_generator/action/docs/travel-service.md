# Travel Service API 文档

旅行服务（ts-travel-service）和普通火车服务（ts-travel2-service）的API文档。

## 目录

- [查询高铁/动车剩余车票](#查询高铁/动车剩余车票)
- [查询普通火车剩余车票](#查询普通火车剩余车票)

---

## 查询高铁/动车剩余车票

查询指定起点、终点和出发日期的车次及剩余车票信息。

### API信息
- **Endpoint**: `/api/v1/travelservice/trips/left`
- **Method**: `POST`
- **Description**: 返回符合条件的车次及剩余车票信息
- **认证**: 不需要

### 请求参数

```json
{
  "startPlace": "string",
  "endPlace": "string",
  "departureTime": "string"
}
```

**参数说明**:
- `startPlace` (string, 必填): 起点站名称
- `endPlace` (string, 必填): 终点站名称
- `departureTime` (string, 必填): 出发日期，格式为日期字符串

### 响应格式

成功响应：
```json
{
  "status": 1,
  "msg": "Success",
  "data": [
    {
      "tripId": {
        "type": "G",
        "number": "1234"
      },
      "trainTypeName": "string",
      "startStation": "string",
      "terminalStation": "string",
      "startTime": "string",
      "endTime": "string",
      "economyClass": 50,
      "confortClass": 50,
      "priceForEconomyClass": "string",
      "priceForConfortClass": "string"
    },
    ...
  ]
}
```

失败响应（参数为空时）：
```json
[]
```

**响应字段说明**:
- `status` (integer): 1表示成功，0表示失败
- `msg` (string): 响应消息
- `data` (array): 车次列表，每个元素包含：
  - `tripId` (object): 车次ID，包含 `type`（车次类型：G/D/K/T/Z）和 `number`（车次号）
  - `trainTypeName` (string): 列车类型名称
  - `startStation` (string): 起点站
  - `terminalStation` (string): 终点站
  - `startTime` (string): 出发时间
  - `endTime` (string): 到达时间
  - `economyClass` (integer): 经济座剩余票数
  - `confortClass` (integer): 舒适座剩余票数
  - `priceForEconomyClass` (string): 经济座价格
  - `priceForConfortClass` (string): 舒适座价格

### Action方法

**方法名**: `query_trips_left()`

**入参**:
- `start_place` (str): 起点站名称
- `end_place` (str): 终点站名称
- `departure_time` (str): 出发日期

**返回值**:
- `list[dict[str, object]]`: 车次列表
  - 成功时返回: `[{"tripId": {...}, "trainTypeName": "...", "economyClass": 50, ...}, ...]`
  - 失败时返回: 空列表 `[]`

### 注意事项

1. **参数验证**: 如果 `startPlace`、`endPlace` 或 `departureTime` 为空，接口会返回空列表
2. **日期格式**: `departureTime` 需要是有效的日期字符串
3. **日期验证**: 系统会验证出发日期是否为今天或之后，过去的日期不会返回结果
4. **车次类型**: `tripId.type` 可能的值包括：G（高铁）、D（动车）、K（快速）、T（特快）、Z（直达）
5. **服务范围**: 此接口仅查询高铁和动车（G/D开头的车次）

---

## 查询普通火车剩余车票

查询指定起点、终点和出发日期的普通火车车次及剩余车票信息。

### API信息
- **Endpoint**: `/api/v1/travel2service/trips/left`
- **Method**: `POST`
- **Description**: 返回符合条件的普通火车车次及剩余车票信息
- **认证**: 不需要

### 请求参数

```json
{
  "startPlace": "string",
  "endPlace": "string",
  "departureTime": "string"
}
```

**参数说明**:
- `startPlace` (string, 必填): 起点站名称
- `endPlace` (string, 必填): 终点站名称
- `departureTime` (string, 必填): 出发日期，格式为日期字符串

### 响应格式

成功响应：
```json
{
  "status": 1,
  "msg": "Success",
  "data": [
    {
      "tripId": {
        "type": "K",
        "number": "1234"
      },
      "trainTypeName": "string",
      "startStation": "string",
      "terminalStation": "string",
      "startTime": "string",
      "endTime": "string",
      "economyClass": 50,
      "confortClass": 50,
      "priceForEconomyClass": "string",
      "priceForConfortClass": "string"
    },
    ...
  ]
}
```


---

## 错误码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 500 | 服务器内部错误 |

---

## 通用注意事项

1. **参数完整性**: 必须提供完整的起点、终点和出发日期
2. **日期有效性**: 出发日期必须是今天或之后的日期
3. **响应格式**: 成功时返回Response包装的列表，参数为空时直接返回空列表
4. **服务选择**: 根据要查询的车次类型选择对应的服务
   - G/D开头的车次 → 使用 `query_trips_left()` (travelservice)
   - K/T/Z等开头的车次 → 使用 `query_trips_left_normal()` (travel2service)

