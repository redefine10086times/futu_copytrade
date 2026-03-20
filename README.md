# Futu CopyTrade - 富途模拟组合跟单系统

自动跟踪富途牛牛公开模拟组合，通过 moomoo OpenD 在真实账户执行交易。

## 风险提示

**使用本程序前，请务必阅读并同意 moomoo 的 API 使用协议：**
- [moomoo OpenAPI 风险披露协议](https://risk-disclosure.us.moomoo.com/index?agreementNo=USOT0027)

**免责声明：**
- 本程序仅供学习交流，不构成任何投资建议
- 自动交易存在风险，可能导致资金损失
- 使用者需自行承担所有交易风险和后果
- 建议先使用模拟盘充分测试后再连接真实账户

---

## 功能特性

- 自动监控富途公开模拟组合持仓变化
- 自动跟单买入/卖出
- 买入后自动挂止损单（固定/跟踪/ATR）
- 邮件通知持仓变化和交易状态
- 夜盘检测变化发邮件，盘前自动执行
- 支持底仓保护，区分跟单持仓和底仓
- 盘前/盘中/盘后不同交易策略

---

## 完整安装教程

### Step 1：安装 Python

**macOS：**

1. 打开终端（Terminal）
2. 安装 Homebrew（如果没有）：
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. 安装 Python：
   ```bash
   brew install python
   ```
4. 验证安装（macOS 用 python3）：
   ```bash
   python3 --version
   ```

**Windows：**

1. 访问 https://www.python.org/downloads/
2. 点击 "Download Python 3.x.x"
3. 运行安装包，**务必勾选 "Add Python to PATH"**
4. 安装完成后打开命令提示符（CMD）验证：
   ```cmd
   python --version
   ```

---

### Step 2：下载本项目

**方式一：Git 克隆**
```bash
git clone https://github.com/yourname/futu-copytrade.git
```

**方式二：直接下载 ZIP**
1. 点击 GitHub 页面右上角 "Code" -> "Download ZIP"
2. 解压到任意目录

**进入项目目录：**

- macOS：打开终端，cd 进入解压后的 futu_copytrade 文件夹
- Windows：在文件资源管理器中打开 futu_copytrade 文件夹，右键空白处选择 **"在终端中打开"**（Windows 11）或 **"Open in Terminal"**

---

### Step 3：安装 Python 依赖

在项目目录的终端中执行：

macOS：
```bash
pip3 install -r requirements.txt
```

Windows：
```cmd
pip install -r requirements.txt
```

---

### Step 4：安装并配置 moomoo OpenD

OpenD 是 moomoo 提供的本地网关程序，本项目通过它连接交易账户。

**4.1 下载 OpenD**

访问 [moomoo OpenD 下载页面](https://www.moomoo.com/download/openD)，选择对应系统版本下载。

**4.2 启动 OpenD（GUI 模式）**

- macOS：解压后进入GUI文件夹双击 `moomoo_OpenD` 运行，会打开图形界面窗口
- Windows：解压后进入GUI文件夹双击 `moomoo_OpenD.exe` 运行，同样打开图形界面

首次启动时，GUI 界面会提示扫码登录，用 moomoo 账号登录即可。登录成功后界面显示连接状态和端口号（默认 11111）。

**运行期间请保持 OpenD 窗口开着，不要关闭。**

**4.3 签署 API 协议（必须）**

点击签署 [OpenAPI 风险披露协议](https://risk-disclosure.us.moomoo.com/index?agreementNo=USOT0027)

未签署协议会导致 API 调用报错，这步不能跳过。

---

### Step 5：配置 config.py

用文本编辑器打开 `config.py`（Windows 可右键用记事本打开），修改以下参数：

```python
# 要跟踪的模拟组合 ID
# 从 URL 获取：https://www.futunn.com/portfolio/183730 -> 183730
PORTFOLIO_ID = "183730"

# 交易解锁密码（moomoo 设置的 6 位数字密码）
TRADE_PASSWORD = "123456"

# 跟单资金（美元），程序按此金额和权重计算买入股数
TOTAL_CAPITAL = 10000.0

# 交易环境：先用 SIMULATE 模拟盘测试，确认无误后改为 REAL
TRADE_ENV = "SIMULATE"

# 邮件通知（可选）
EMAIL_ENABLED = True
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"   # Gmail 应用专用密码
EMAIL_RECEIVER = "your_email@gmail.com"

# 止损配置
# "none" 不挂止损, "fixed" 固定比例, "trailing" 跟踪止损
STOP_LOSS_MODE = "trailing"
TRAIL_VALUE = 3    # 跟踪止损回撤比例 3%

# 盘前卖出模式
# "always" 盘前正常卖出
# "never"  盘前只买不卖
# "same_count" 5只->5只换仓时不卖，其他情况正常卖出
PREMARKET_SELL_MODE = "never"
```

**获取模拟组合 ID：**
1. 打开 [富途牛牛网页版](https://www.futunn.com/)
2. 找到要跟踪的公开模拟组合
3. URL 中的数字即为组合 ID，如 `https://www.futunn.com/portfolio/183730` 中的 `183730`

**获取 Gmail 应用专用密码：**
1. 登录 Google 账户 -> 安全性
2. 开启两步验证
3. 搜索"应用专用密码"，生成一个 16 位密码
4. 填入 `EMAIL_PASSWORD`

---

### Step 6：测试 OpenD 连接

**6.1 测试账户连接（test.py）**

先确认 OpenD 能正常连接并检测到账户：

macOS：
```bash
python3 test.py
```

Windows：
```cmd
python test.py
```

成功输出示例：
```
--- 成功获取账户列表 ---
   acc_id  trd_env trd_market
0  123456     REAL         US
1  789012  SIMULATE        US

trd_env 集合: {'REAL', 'SIMULATE'}
检测到 REAL（实盘）账户
```

如果只看到 SIMULATE 没有 REAL，说明 OpenD 当前会话没有实盘权限，检查是否已签署 API 协议。

**6.2 测试持仓查询（test_positions.py）**

确认能正常读取账户持仓：

macOS：
```bash
python3 test_positions.py
```

Windows：
```cmd
python test_positions.py
```

成功输出示例：
```
已连接 OpenD
当前持仓:
  US.AAPL: 10 股
  US.TSLA: 5 股
```

如果报错，检查：
- OpenD 是否正在运行
- 是否已签署 API 协议
- TRADE_PASSWORD 是否正确

---

### Step 7：启动跟单程序

建议先用干跑模式测试，确认检测逻辑正常后再正式运行。

macOS：
```bash
python3 main.py --dry    # 干跑模式：只检测变化，不实际下单
python3 main.py --once   # 只检查一次（测试用）
python3 main.py          # 正式启动（持续轮询）
```

Windows：
```cmd
python main.py --dry
python main.py --once
python main.py
```

**首次启动交互流程：**

程序启动后会进入初始化，逐一询问每只股票的跟单设置：

```
==================================================
启动初始化
==================================================

当前组合持仓 (5 只):
  US.AAPL Apple 权重=20.0%
  US.TSLA Tesla 权重=20.0%
  ...

当前账户持仓 (2 只):
  US.AAPL: 15 股

请为组合中的每只股票设置跟单状态:
--------------------------------------------------

  US.AAPL Apple (持有 15 股)
  跟单数量 (回车=0, all=全部): 10
  # 输入 10 -> 15 股中 10 股跟单，5 股为底仓（不会被自动卖出）

  US.TSLA Tesla (未持有, 权重=20.0%)
  是否买入? (y/n): y
  # 盘中输入 y -> 立即买入；夜盘输入 y -> 记录待买入，盘前自动执行
```

初始化完成后程序进入轮询，每 30 秒检查一次组合变化。

---

## 交易时段说明

| 时段 | 时间 (美东 ET) | 行为 |
|------|---------------|------|
| 夜盘 | 20:00 - 次日 4:00 | 只发邮件通知，不交易 |
| 盘前 | 4:00 - 9:30 | 执行买入，卖出根据 PREMARKET_SELL_MODE 配置 |
| 盘中 | 9:30 - 16:00 | 正常买卖（市价单） |
| 盘后 | 16:00 - 20:00 | 正常买卖（限价单） |
| 周末 | 周五 20:00 - 周日 16:00 | 暂停轮询 |

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `config.py` | 配置文件，所有参数在这里修改 |
| `main.py` | 主程序入口 |
| `monitor.py` | 组合监控模块 |
| `trader.py` | 交易执行模块 |
| `stoploss.py` | 止损模块 |
| `notify.py` | 邮件通知模块 |
| `test.py` | 测试账户连接和实盘检测 |
| `test_positions.py` | 测试持仓查询 |
| `snapshot.json` | 组合持仓快照（自动生成） |
| `copytrade_positions.json` | 跟单持仓记录（自动生成） |
| `copytrade.log` | 运行日志（自动生成） |

---

## 常见问题

**Q: 提示 "No one available account"**
A: OpenD 未登录或未签署 API 协议。重新打开 OpenD 登录，并在 moomoo 客户端签署协议。

**Q: 提示 "解锁交易失败"**
A: TRADE_PASSWORD 填写错误，检查 config.py 中的密码。

**Q: 市价单报错 "非盘中时段不允许市价单"**
A: 程序会自动在盘前盘后使用限价单，确保使用最新版本代码。

**Q: 如何保护底仓不被卖出？**
A: 初始化时，对于已持有的股票，输入跟单数量时填小于实际持仓的数字，差额部分即为底仓，程序不会自动卖出底仓。

**Q: 如何切换到真实账户？**
A: 模拟盘测试无误后，将 TRADE_ENV = "SIMULATE" 改为 TRADE_ENV = "REAL"，重启程序。

---

## License

MIT
