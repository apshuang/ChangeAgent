# Travel Service API 文档

旅行服务（ts-travel-service）、普通火车服务（ts-travel2-service）、保险服务（ts-assurance-service）、食物服务（ts-food-service）和预订服务（ts-preserve-service）等一系列与旅行订票相关服务的API文档。

## 目录

- [查询高铁/动车剩余车票](#查询高铁/动车剩余车票)
- [查询普通火车剩余车票](#查询普通火车剩余车票)
- [获取保险类型](#获取保险类型)
- [获取所有食物信息](#获取所有食物信息)
- [预订动车车票](#预订动车车票)
- [预订普通火车车票](#预订普通火车车票)

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

## 获取保险类型

获取系统中所有可用的保险类型。

### API信息
- **Endpoint**: `/api/v1/assuranceservice/assurances/types`
- **Method**: `GET`
- **Description**: 获取所有可用的保险类型
- **认证**: 需要，需要在header中带上token，比如`{"Authorization": f"Bearer {token}"}`

### 请求参数

无

### 响应格式

成功响应：
```json
{
  "status": 1,
  "msg": "Find All Assurance",
  "data": [
    {
      "index": 1,
      "name": "Traffic Accident Assurance",
      "price": 3.0
    },
    ...
  ]
}
```

**响应字段说明**:
- `status` (integer): 1表示成功
- `msg` (string): 响应消息，通常为 "Find All Assurance"
- `data` (array): 保险类型列表，每个元素包含：
  - `index` (integer): 保险类型索引，用于购买保险时指定类型
  - `name` (string): 保险类型名称
  - `price` (float): 保险价格

### Action方法

**方法名**: `get_assurance_types()`

**入参**:
- `token` (str): 认证token（需要先通过login方法获取）

**返回值**:
- `list[dict[str, object]]`: 保险类型列表
  - 成功时返回: `[{"index": 1, "name": "Traffic Accident Assurance", "price": 3.0}, ...]`
  - 失败时返回: 空列表 `[]`

### 注意事项

- 需要先登录获取token，然后在请求头中添加：`Authorization: Bearer {token}`
- 保险类型的 `index` 字段用于后续购买保险时指定保险类型
- 返回的保险类型是系统中所有可用的保险类型，不区分用户

---

## 获取所有食物信息

获取指定日期、起点、终点和车次的所有食物信息，包括列车上的食物和沿途站点的食物商店。

### API信息
- **Endpoint**: `/api/v1/foodservice/foods/{date}/{startStation}/{endStation}/{tripId}`
- **Method**: `GET`
- **Description**: 获取指定车次的所有食物信息，包括列车食物和站点食物商店
- **认证**: 不需要

### 请求参数

**路径参数**:
- `date` (string, 必填): 日期，格式：YYYY-MM-DD（例如：2024-12-25）
- `startStation` (string, 必填): 起点站名称（例如：shanghai）
- `endStation` (string, 必填): 终点站名称（例如：suzhou）
- `tripId` (string, 必填): 车次ID（例如：D1345, G1234等）

### 响应格式

成功响应：
```json
{
  "status": 1,
  "msg": "Get All Food Success",
  "data": {
    "trainFoodList": [
      {
        "foodName": "Spicy hot noodles",
        "price": 5.0
      },
      {
        "foodName": "Soup",
        "price": 3.7
      },
      {
        "foodName": "Oily bean curd",
        "price": 2.0
      }
    ],
    "foodStoreListMap": {
      "suzhou": [
        {
          "id": "c160d36d-b5f0-4cae-affc-fa2dba530491",
          "stationName": "suzhou",
          "storeName": "Roman Holiday",
          "telephone": "3769464",
          "businessTime": "09:00-23:00",
          "deliveryFee": 15.0,
          "foodList": [
            {
              "foodName": "Big Burger",
              "price": 1.2
            },
            {
              "foodName": "Bone Soup",
              "price": 2.5
            }
          ]
        }
      ],
      "shanghai": [
        {
          "id": "9c2e50bc-a1e8-4736-b0fe-b8966325d779",
          "stationName": "shanghai",
          "storeName": "Good Taste",
          "telephone": "6228480012",
          "businessTime": "08:00-21:00",
          "deliveryFee": 10.0,
          "foodList": [
            {
              "foodName": "Rice",
              "price": 1.2
            },
            {
              "foodName": "Chicken Soup",
              "price": 2.5
            }
          ]
        }
      ]
    }
  }
}
```

**响应字段说明**:
- `status` (integer): 1表示成功
- `msg` (string): 响应消息，通常为 "Get All Food Success"
- `data` (object): 食物数据对象，包含：
  - `trainFoodList` (array): 列车上的食物列表，每个元素包含：
    - `foodName` (string): 食物名称
    - `price` (float): 食物价格
  - `foodStoreListMap` (object): 按站点名称分组的食物商店列表，键为站点名称，值为该站点的商店数组，每个商店包含：
    - `id` (string): 商店ID（UUID格式）
    - `stationName` (string): 站点名称
    - `storeName` (string): 商店名称
    - `telephone` (string): 联系电话
    - `businessTime` (string): 营业时间（格式：HH:MM-HH:MM）
    - `deliveryFee` (float): 配送费
    - `foodList` (array): 该商店的食物列表，每个元素包含：
      - `foodName` (string): 食物名称
      - `price` (float): 食物价格

### Action方法

**方法名**: `get_all_foods()`

**入参**:
- `date` (str): 日期，格式：YYYY-MM-DD
- `start_station` (str): 起点站名称
- `end_station` (str): 终点站名称
- `trip_id` (str): 车次ID

**返回值**:
- `dict[str, object]`: 食物数据对象
  - 成功时返回: `{"trainFoodList": [...], "foodStoreListMap": {...}}`
  - 失败时返回: 空字典 `{}`

### 注意事项

- 此接口不需要认证，可以直接调用
- `tripId` 应该是有效的车次ID（例如：G1234, D1345等）
- 返回的食物信息包括：
  1. **列车食物**（`trainFoodList`）：列车上提供的食物
  2. **站点食物商店**（`foodStoreListMap`）：沿途各站点的食物商店，按站点名称分组
- `foodStoreListMap` 是一个对象，键为站点名称，值为该站点的商店数组
- 每个商店都有独立的配送费（`deliveryFee`）
- 日期必须为有效的YYYY-MM-DD格式
- `startStation` 和 `endStation` 应该使用正确的站点名称

---

## 预订动车车票

预订指定车次的动车车票，支持选择座位类型、保险、食物等附加服务。

### API信息
- **Endpoint**: `/api/v1/preserveservice/preserve` (ts-preserve-service)
- **Method**: `POST`
- **Description**: 预订高铁/动车车票
- **认证**: 需要，需要在header中带上token，比如`{"Authorization": f"Bearer {token}"}`

### 请求参数

```json
{
  "accountId": "4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f",
  "contactsId": "38e3e89a-fc5a-45f8-9deb-8352c4c3c606",
  "tripId": "D1345",
  "seatType": "2",
  "date": "2025-12-05",
  "from": "shanghai",
  "to": "suzhou",
  "assurance": "1",
  "foodType": 2,
  "stationName": "suzhou",
  "storeName": "Roman Holiday",
  "foodName": "Soup",
  "foodPrice": 3.7
}
```

**参数说明**:
- `accountId` (string, 必填): 账户ID（UUID格式），可通过登录接口获取
- `contactsId` (string, 必填): 联系人ID（UUID格式），可通过联系人查询接口获取
- `tripId` (string, 必填): 车次ID（字符串格式，例如：G1234, D1345等）
- `seatType` (string, 必填): 座位类型，`"1"`表示经济座，`"2"`表示舒适座
- `date` (string, 必填): 出发日期，格式：YYYY-MM-DD
- `from` (string, 必填): 起点站名称
- `to` (string, 必填): 终点站名称
- `assurance` (string, 必填): 保险类型索引（字符串格式），`"0"`表示不购买保险，其它索引都是对应的保险号
- `foodType` (integer, 可选): 食物类型（数字格式），`0`表示不订购食物，其它索引都是对应的食物类型
- `stationName` (string, 可选): 站点名称（用于食物配送），订购食物时必填
- `storeName` (string, 可选): 商店名称（用于食物配送），订购食物时必填
- `foodName` (string, 可选): 食物名称，订购食物时必填
- `foodPrice` (number, 可选): 食物价格，订购食物时必填

### 响应格式

成功响应：
```json
{
  "status": 1,
  "msg": "Success.",
  "data": "Success"
}
```

失败响应：
```json
{
  "status": 0,
  "msg": "Error message",
  "data": null
}
```

### Action方法

**方法名**: `preserve_ticket()`

**入参**:
- `account_id` (str): 账户ID（UUID格式）
- `contacts_id` (str): 联系人ID（UUID格式）
- `trip_id` (str): 车次ID（字符串格式，例如：G1234, D1345等）
- `seat_type` (str): 座位类型，`"1"`表示舒适座，`"2"`表示经济座
- `date` (str): 出发日期，格式：YYYY-MM-DD
- `from_station` (str): 起点站名称
- `to_station` (str): 终点站名称
- `assurance` (str): 保险类型索引，`"0"`表示不购买保险，`"1"`表示购买保险
- `token` (str): 认证token（需要先通过login方法获取）
- `food_type` (int, 可选): 食物类型，`0`表示不订购食物，`2`表示订购食物，默认为0
- `station_name` (str, 可选): 站点名称（用于食物配送）
- `store_name` (str, 可选): 商店名称（用于食物配送）
- `food_name` (str, 可选): 食物名称
- `food_price` (float, 可选): 食物价格

**返回值**:
- `dict[str, object]`: 预订响应数据
  - 成功时返回: `{"status": 1, "msg": "Success.", "data": "Success"}`
  - 失败时返回: `{"status": 0, "msg": "Error message", "data": null}` 或空字典 `{}`

### 注意事项

- 预订接口需要先登录获取token，然后在请求头中添加：`Authorization: Bearer {token}`
- `accountId` 和 `contactsId` 必须是有效的UUID格式
  - `accountId` 可以通过登录接口的响应中获取（`data.userId`）
  - `contactsId` 可以通过联系人查询接口获取（`/api/v1/contactservice/contacts/account/{accountId}`）
- `tripId` 应该是有效的车次ID，可以通过查询剩余车票接口获取
- `seatType` 必须是字符串格式：`"1"`（经济座）或 `"2"`（舒适座）
- `assurance` 必须是字符串格式：`"0"`（不购买）或 `"1"`（购买）
- 如果 `foodType` 不为0，则需要提供 `stationName`、`storeName`、`foodName` 和 `foodPrice` 参数
- 日期必须为有效的YYYY-MM-DD格式，且必须是今天或之后的日期
- 预订成功后，响应中的 `data` 字段为字符串 `"Success"`，不是订单ID对象
- 该接口仅支持高铁/动车（G/D列车）的预订，普通火车需要使用 `preserve_other` 接口

---

## 预订普通火车车票

预订指定车次的普通火车车票（K/T/Z等非G/D列车），支持选择座位类型、保险、食物等附加服务。

### API信息
- **Endpoint**: `/api/v1/preserveotherservice/preserveOther` (ts-preserve-other-service)
- **Method**: `POST`
- **Description**: 预订普通火车车票
- **认证**: 需要，需要在header中带上token，比如`{"Authorization": f"Bearer {token}"}`

### 请求参数

```json
{
  "accountId": "4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f",
  "contactsId": "38e3e89a-fc5a-45f8-9deb-8352c4c3c606",
  "tripId": "Z1235",
  "seatType": "2",
  "date": "2025-12-05",
  "from": "xuzhou",
  "to": "beijing",
  "assurance": "1",
  "foodType": 1,
  "foodName": "Bone Soup",
  "foodPrice": 2.5,
  "stationName": "",
  "storeName": ""
}
```

**参数说明**:
- `accountId` (string, 必填): 账户ID（UUID格式），可通过登录接口获取
- `contactsId` (string, 必填): 联系人ID（UUID格式），可通过联系人查询接口获取
- `tripId` (string, 必填): 车次ID（字符串格式，例如：K1234, T5678, Z1235等）
- `seatType` (string, 必填): 座位类型，`"1"`表示舒适座，`"2"`表示经济座
- `date` (string, 必填): 出发日期，格式：YYYY-MM-DD
- `from` (string, 必填): 起点站名称
- `to` (string, 必填): 终点站名称
- `assurance` (string, 必填): 保险类型索引（字符串格式），`"0"`表示不购买保险，其它索引都是对应的保险号
- `foodType` (integer, 可选): 食物类型（数字格式），`0`表示不订购食物，其它索引都是对应的食物类型
- `foodName` (string, 可选): 食物名称，订购食物时必填
- `foodPrice` (number, 可选): 食物价格，订购食物时必填
- `stationName` (string, 可选): 站点名称（用于食物配送），可以为空字符串
- `storeName` (string, 可选): 商店名称（用于食物配送），可以为空字符串

### 响应格式

成功响应：
```json
{
  "status": 1,
  "msg": "Success.",
  "data": "Success"
}
```

失败响应：
```json
{
  "status": 0,
  "msg": "Error message",
  "data": null
}
```

### Action方法

**方法名**: `preserve_other_ticket()`

**入参**:
- `account_id` (str): 账户ID（UUID格式）
- `contacts_id` (str): 联系人ID（UUID格式）
- `trip_id` (str): 车次ID（字符串格式，例如：K1234, T5678, Z1235等）
- `seat_type` (str): 座位类型，`"1"`表示舒适座，`"2"`表示经济座
- `date` (str): 出发日期，格式：YYYY-MM-DD
- `from_station` (str): 起点站名称
- `to_station` (str): 终点站名称
- `assurance` (str): 保险类型索引，`"0"`表示不购买保险，其它索引都是对应的保险号
- `token` (str): 认证token（需要先通过login方法获取）
- `food_type` (int, 可选): 食物类型，`0`表示不订购食物，其它索引都是对应的食物类型，默认为0
- `food_name` (str, 可选): 食物名称
- `food_price` (float, 可选): 食物价格
- `station_name` (str, 可选): 站点名称（用于食物配送），可以为空字符串
- `store_name` (str, 可选): 商店名称（用于食物配送），可以为空字符串

**返回值**:
- `dict[str, object]`: 预订响应数据
  - 成功时返回: `{"status": 1, "msg": "Success.", "data": "Success"}`
  - 失败时返回: `{"status": 0, "msg": "Error message", "data": null}` 或空字典 `{}`

### 注意事项

- 预订接口需要先登录获取token，然后在请求头中添加：`Authorization: Bearer {token}`
- `accountId` 和 `contactsId` 必须是有效的UUID格式
  - `accountId` 可以通过登录接口的响应中获取（`data.userId`）
  - `contactsId` 可以通过联系人查询接口获取（`/api/v1/contactservice/contacts/account/{accountId}`）
- `tripId` 应该是有效的车次ID，可以通过查询剩余车票接口获取（使用 `travel2service`）
- `seatType` 必须是字符串格式：`"1"`（舒适座）或 `"2"`（经济座）
- `assurance` 必须是字符串格式：`"0"`（不购买）或其它保险类型索引
- 如果 `foodType` 不为0，则需要提供 `foodName` 和 `foodPrice` 参数
- `stationName` 和 `storeName` 可以为空字符串，即使订购食物时也可以为空
- 日期必须为有效的YYYY-MM-DD格式，且必须是今天或之后的日期
- 预订成功后，响应中的 `data` 字段为字符串 `"Success"`，不是订单ID对象
- 该接口仅支持普通火车（K/T/Z等非G/D列车）的预订，高铁/动车需要使用 `preserve` 接口

---

## 错误码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 500 | 服务器内部错误 |

---

## 服务说明

### ts-travel-service
- 主要负责高铁和动车（G/D列车）的车次和剩余车票查询
- 提供车次信息、路线信息、列车类型等查询功能
- 所有API返回都使用Response包装：`{"status": 1, "msg": "...", "data": ...}`

### ts-travel2-service
- 主要负责普通火车（非G/D列车）的车次和剩余车票查询
- 提供普通火车的车次信息、路线信息、列车类型等查询功能
- 所有API返回都使用Response包装：`{"status": 1, "msg": "...", "data": ...}`

### ts-food-service
- 主要负责食物信息管理和食物订单管理
- 提供食物查询、食物订单创建、更新、删除等功能
- 所有API返回都使用Response包装：`{"status": 1, "msg": "...", "data": ...}`

### ts-preserve-service
- 主要负责高铁/动车（G/D列车）的车票预订
- 提供车票预订功能，支持选择座位类型、保险、食物等附加服务
- 所有API返回都使用Response包装：`{"status": 1, "msg": "...", "data": ...}`
- 预订操作会调用多个其他服务（车次信息、座位分配、订单创建等）

### ts-preserve-other-service
- 主要负责普通火车（K/T/Z等非G/D列车）的车票预订
- 提供普通火车车票预订功能，支持选择座位类型、保险、食物等附加服务
- 所有API返回都使用Response包装：`{"status": 1, "msg": "...", "data": ...}`
- 预订操作会调用多个其他服务（车次信息、座位分配、订单创建等）

### 服务选择说明

- **高铁/动车（G/D列车）**: 使用 `ts-travel-service`，接口前缀为 `/api/v1/travelservice`
- **普通火车（K/T/Z等）**: 使用 `ts-travel2-service`，接口前缀为 `/api/v1/travel2service`
- **食物服务**: 使用 `ts-food-service`，接口前缀为 `/api/v1/foodservice`
- **预订服务（G/D列车）**: 使用 `ts-preserve-service`，接口前缀为 `/api/v1/preserveservice`
- **预订服务（普通火车）**: 使用 `ts-preserve-other-service`，接口前缀为 `/api/v1/preserveotherservice`
- 两个旅行服务的接口格式和参数完全相同，只是查询的车次类型不同
- 两个预订服务的接口格式和参数基本相同，只是预订的车次类型不同

---

## 通用注意事项

1. **参数完整性**: 必须提供完整的起点、终点和出发日期
2. **日期有效性**: 出发日期必须是今天或之后的日期
3. **响应格式**: 成功时返回Response包装的列表，参数为空时直接返回空列表
4. **服务选择**: 根据要查询的车次类型选择对应的服务
   - G/D开头的车次 → 使用 `query_trips_left()` (travelservice)
   - K/T/Z等开头的车次 → 使用 `query_trips_left_normal()` (travel2service)
5. **食物查询**: 获取食物信息时需要提供有效的车次ID和日期
6. **预订车票**: 预订前需要先获取有效的 `accountId` 和 `contactsId`
   - `accountId` 可通过登录接口获取
   - `contactsId` 可通过联系人查询接口获取
7. **预订响应**: 预订成功后，响应中的 `data` 字段为字符串 `"Success"`，不是订单ID对象
8. **预订服务选择**: 根据要预订的车次类型选择对应的预订服务
   - G/D开头的车次 → 使用 `preserve_ticket()` (preserveservice)
   - K/T/Z等开头的车次 → 使用 `preserve_other_ticket()` (preserveotherservice)

