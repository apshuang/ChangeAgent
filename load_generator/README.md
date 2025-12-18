# TrainTicket 负载生成器

基于 Locust 实现的 TrainTicket 微服务系统负载生成器，采用便于扩展的模块化设计，用于自动生成工作负载并收集正常运行场景下的数据。

## 功能特性

- ✅ **模块化架构**：采用 Action 和 Flow 设计模式，职责清晰，易于扩展和维护
- ✅ **真实业务流程**：模拟完整的用户购票流程（查票 → 登录 → 选择座位/保险/食物 → 订票）
- ✅ **灵活配置**：支持高铁/动车（G/D）和普通列车的完整购票流程
- ✅ **智能随机化**：自动随机选择起点/终点、座位类型、保险、食物等，模拟真实用户行为
- ✅ **路线验证**：基于配置的路线信息确保查询的车次路线真实存在
- ✅ **易于扩展**：清晰的扩展流程，从 API 文档到 Action，再到 Flow，最后集成到负载测试

## 项目结构

```
load_generator/
├── action/                    # Action 模块 - 按功能分类的 API 操作类，每个action对应一个原子操作（一个API）
├── flow/                      # Flow 模块 - 业务流程组合
├── test/                      # 测试目录 - 用于测试对应的功能
├── scripts/                   # 工具脚本目录
├── train-ticket.wiki/         # TrainTicket 系统文档（参考用）
├── config.py                  # 配置文件（服务器地址、车站信息、用户信息等）
├── utils.py                   # 工具函数（随机数据生成、车次选择等）
├── locustfile.py              # Locust 主文件，定义负载测试任务
├── requirements.txt           # Python 依赖包
└── README.md                  # 本文档
```

## 文件夹说明

### `action/` - Action 模块

Action 模块按功能分类组织，每个 Action 类负责一类 API 操作，部分如下：

- **`docs/`**：存放各服务的 API 文档，详细记录每个 API 的请求参数和返回格式
- **`base_action.py`**：所有 Action 的基类，提供通用的 HTTP 请求方法（`_post`, `_get`, `_put`, `_delete`）
- **`auth_action.py`**：认证和用户管理相关的 API 操作（登录、注册、查询用户等）

### `flow/` - Flow 模块

Flow 模块组合多个 Action 完成完整的业务流程：

- **`base_flow.py`**：所有 Flow 的基类，初始化所有 Action 实例，提供通用辅助方法
- **`simple_flow.py`**：简单流程，包含单个或少量操作（如只查票、只登录、只注册）
- **`travel_flow.py`**：完整订票流程，包含查票、登录、选择座位/保险/食物、订票等完整步骤

### `test/` - 测试目录

- **`test_flow.py`**：Flow 测试脚本，用于在集成到 Locust 之前验证单个 Flow 的功能是否正确

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置系统地址

编辑 `config.py` 或使用环境变量：

```bash
export TRAINTICKET_BASE_URL=http://your-trainticket-host:32677
```

### 3. 测试单个 Flow

在集成到 Locust 之前，先测试单个 Flow 确保功能正常：

```bash
# 测试查询流程
python test/test_flow.py query

# 测试登录流程
python test/test_flow.py login

# 测试订票流程
python test/test_flow.py booking
```

### 4. 运行负载测试

```bash
# 无头模式运行（快速测试）
locust -f locustfile.py --host=http://10.10.1.98:32677 --headless -u 10 -r 3 -t 30s

# 参数说明：
# -u 10: 10个并发用户
# -r 3: 每秒启动3个用户（ramp-up rate）
# -t 30s: 运行30秒

# 持续运行（后台运行）
nohup locust -f locustfile.py --host=http://10.10.1.98:32677 --headless -u 100 -r 10 > locust.log 2>&1 &
```

## 如何扩展

### 扩展流程概览

扩展新功能的完整流程：

1. **编写 API 文档** → 2. **实现 Action** → 3. **实现 Flow** → 4. **编写测试** → 5. **集成到 Locust**

---

### 步骤 1：编写 API 文档

在 `action/docs/` 目录下创建或更新对应的服务文档（如 `payment-service.md`），详细记录：

- API 端点信息（URL、HTTP 方法）
- 请求参数（参数名、类型、是否必填、说明）
- 响应格式（成功和失败的响应结构）
- 认证要求（是否需要 token）

---

### 步骤 2：实现 Action

#### 2.1 创建 Action 文件

在 `action/` 目录下创建新的 Action 文件，例如 `payment_action.py`：

```python
from .base_action import BaseAction

class PaymentAction(BaseAction):
    """支付相关的API操作"""
    
    def pay_order(self, order_id: str, user_id: str, token: str) -> dict[str, object]:
        """
        支付订单
        
        Args:
            order_id: 订单ID
            user_id: 用户ID
            token: 认证token
            
        Returns:
            支付结果
        """
        data = {
            "orderId": order_id,
            "userId": user_id
        }
        headers = {"Authorization": f"Bearer {token}"}
        return self._post("/api/v1/payservice/pay", data, headers=headers)
```

#### 2.2 导出 Action

在 `action/__init__.py` 中添加：

```python
from .payment_action import PaymentAction
__all__ = [..., "PaymentAction"]
```

#### 2.3 在 BaseFlow 中初始化

在 `flow/base_flow.py` 中添加：

```python
from action import PaymentAction

class BaseFlow:
    def __init__(self, client):
        # ... 现有代码 ...
        self.payment = PaymentAction(client)  # 添加这行
```

---

### 步骤 3：实现 Flow

#### 3.1 创建 Flow 文件

在 `flow/` 目录下创建新的 Flow 文件，例如 `payment_flow.py`：

```python
import logging
from .base_flow import BaseFlow

logger = logging.getLogger(__name__)

class PaymentFlow(BaseFlow):
    """支付流程 - 登录 -> 查询订单 -> 支付"""
    
    def execute(
        self,
        order_id: str | None = None,
        username: str | None = None,
        password: str | None = None
    ) -> dict[str, object]:
        """
        执行支付流程
        
        Args:
            order_id: 订单ID（可选，如果不提供则需要先查询）
            username: 用户名（可选）
            password: 密码（可选）
            
        Returns:
            支付结果
        """
        result = {"success": False, "error": None}
        
        try:
            # 1. 登录获取token
            if username and password:
                login_result = self.auth.login(username, password)
                # ... 处理登录结果 ...
            
            # 2. 查询订单（如果需要）
            if not order_id:
                # ... 查询订单逻辑 ...
                pass
            
            # 3. 支付订单
            payment_result = self.payment.pay_order(order_id, user_id, token)
            # ... 处理支付结果 ...
            
            result["success"] = True
        except Exception as e:
            logger.error(f"支付流程失败: {str(e)}", exc_info=True)
            result["error"] = str(e)
        
        return result
```

#### 3.2 导出 Flow

在 `flow/__init__.py` 中添加：

```python
from .payment_flow import PaymentFlow
__all__ = [..., "PaymentFlow"]
```

---

### 步骤 4：编写测试

在 `test/test_flow.py` 中添加测试用例：

```python
# 在 main() 函数中添加
elif flow_name == "payment":
    print("测试 PaymentFlow")
    flow = PaymentFlow(client)
    result = flow.execute()
    print_result(result)
```

然后运行测试：

```bash
python test/test_flow.py payment
```

确保 Flow 功能正常后再进行下一步。

---

### 步骤 5：集成到 Locust

在 `locustfile.py` 中添加新的任务：

```python
from flow import PaymentFlow

class TrainTicketUser(HttpUser):
    # ... 现有代码 ...
    
    @task(1)  # 权重为1，表示执行频率
    def payment_flow(self):
        """执行支付流程"""
        flow = PaymentFlow(self.client)
        result = flow.execute()
        
        if result["success"]:
            logger.info(f"支付流程完成，订单: {result.get('order_id')}")
        else:
            logger.warning(f"支付流程失败: {result.get('error')}")
```

---

## 设计原则

### Action 设计原则

1. **单一职责**：每个 Action 类只负责一类功能（认证、旅行、支付等）
2. **继承 BaseAction**：所有 Action 继承 `BaseAction`，使用通用的 HTTP 请求方法
3. **类型提示**：使用 Python 3.11+ 的类型提示（`str | None`, `dict[str, object]` 等）
4. **文档先行**：先编写 API 文档，明确参数和返回格式，再实现代码

### Flow 设计原则

1. **组合 Action**：Flow 通过组合多个 Action 完成业务流程
2. **数据准备**：Flow 内部负责数据准备（随机生成或使用参数）
3. **错误处理**：每个 Flow 都应该有完善的错误处理和日志记录
4. **返回格式统一**：所有 Flow 的 `execute` 方法返回统一的字典格式：
   ```python
   {
       "success": bool,
       "data": ...,      # 可选
       "error": str,      # 可选
       ...
   }
   ```

---

## 注意事项

1. **用户账号**：确保 `config.py` 中配置的用户账号在 TrainTicket 系统中存在且可用
2. **系统地址**：确保 `BASE_URL` 配置正确，指向已部署的 TrainTicket 系统
3. **网络连接**：确保负载生成器能够访问 TrainTicket 系统的所有服务
4. **数据清理**：长时间运行可能会产生大量测试数据，需要定期清理
5. **路线配置**：确保 `config.py` 中的路线配置（`ROUTES_HIGH_SPEED`, `ROUTES_NORMAL`）与实际系统一致

---

## 故障排查

### 连接错误

- 检查 TrainTicket 系统是否正常运行
- 检查 `BASE_URL` 配置是否正确
- 检查网络连接和防火墙设置

### 认证失败

- 检查用户名和密码是否正确
- 检查用户账号是否在系统中存在
- 检查 token 是否有效

### 查票失败

- 检查是否有可用的车次数据
- 检查日期格式是否正确（YYYY-MM-DD）
- 检查路线配置是否正确

### 订票失败

- 检查是否有余票
- 检查联系人ID是否正确
- 检查用户是否有足够的余额
- 检查座位类型、保险、食物参数是否正确

---

## 许可证

本项目用于 AIOps 研究和 TrainTicket 系统测试。
