# LinkedIn Cat CLI 命令详解

LinkedIn Cat 提供了功能丰富的命令行界面，使用 Typer 框架构建。

## 安装和运行

```bash
# 方式 1: 直接运行模块
python -m linkedin_cat.cli.app

# 方式 2: 如果安装了包
linkedincat

# 方式 3: 通过 Python 调用
python -c "from linkedin_cat import run_cli; run_cli()"
```

---

## 全局选项

```bash
linkedincat --help         # 显示帮助信息
linkedincat --version      # 显示版本（如果支持）
```

---

## 命令列表

| 命令 | 说明 |
|------|------|
| `init` | 初始化工作目录 |
| `send` | 发送消息/连接请求 |
| `status` | 查看联系人状态 |
| `reset` | 重置缓存状态 |
| `export` | 导出历史记录 |
| `version` | 显示版本信息 |

---

## init - 初始化工作目录

创建推荐的目录结构和配置文件。

```bash
linkedincat init [OPTIONS]
```

**选项:**
| 选项 | 说明 |
|------|------|
| `--path`, `-p` | 初始化路径，默认当前目录 |

**示例:**

```bash
# 在当前目录初始化
linkedincat init

# 在指定目录初始化
linkedincat init --path ./my_project
```

**创建的内容:**
```
project/
├── config.yaml           # 配置文件
├── message/
│   └── default.txt       # 默认消息模板
├── urls/
│   └── demo.txt          # 示例 URL 文件
├── cache/                # 缓存目录
└── logs/                 # 日志目录
```

---

## send - 发送消息

批量发送消息或连接请求。

```bash
linkedincat send COOKIES MESSAGE URLS [OPTIONS]
```

**参数:**
| 参数 | 说明 |
|------|------|
| `COOKIES` | cookies.json 文件路径 |
| `MESSAGE` | 消息模板文件路径 |
| `URLS` | URL 列表文件路径 |

**选项:**
| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--headless` | bool | false | 无头模式运行 |
| `--dry-run` | bool | false | 仅模拟，不实际发送 |
| `--max` | int | 50 | 本次最大发送数量 |
| `--delay-min` | float | 3.0 | 最小延迟（秒） |
| `--delay-max` | float | 8.0 | 最大延迟（秒） |
| `--config` | str | None | 配置文件路径 |

**示例:**

```bash
# 基本用法
linkedincat send cookies.json message.txt urls.txt

# 无头模式 + 限制数量
linkedincat send cookies.json message.txt urls.txt --headless --max 20

# 干运行模式（不实际发送）
linkedincat send cookies.json message.txt urls.txt --dry-run

# 使用配置文件
linkedincat send cookies.json message.txt urls.txt --config config.yaml
```

**消息模板格式:**

```text
Hi {{name|there}},

I noticed your experience at {{company|your company}}.
I'd love to connect!

Best regards
```

**URL 文件格式:**

```text
# 这是注释
https://www.linkedin.com/in/user-1/
https://www.linkedin.com/in/user-2/

# 空行会被忽略
https://www.linkedin.com/in/user-3/
```

---

## status - 查看状态

查看联系人或缓存的状态。

```bash
linkedincat status [URLS] [OPTIONS]
```

**参数:**
| 参数 | 说明 |
|------|------|
| `URLS` | URL 列表文件（可选） |

**选项:**
| 选项 | 说明 |
|------|------|
| `--url`, `-u` | 查看单个 URL 的状态 |
| `--stats` | 只显示统计信息 |
| `--cache-dir` | 缓存目录路径 |

**示例:**

```bash
# 查看缓存统计
linkedincat status

# 查看 URL 文件中所有联系人的状态
linkedincat status urls.txt

# 查看单个 URL 状态
linkedincat status --url "https://linkedin.com/in/user"

# 只显示统计
linkedincat status --stats
```

**输出示例:**

```
📊 缓存统计
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总联系人:     150
已阻止:       5
冷却中:       45
可发送:       100
缓存大小:     2.3 MB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## reset - 重置状态

重置联系人缓存状态。

```bash
linkedincat reset [OPTIONS]
```

**选项:**
| 选项 | 说明 |
|------|------|
| `--url`, `-u` | 重置单个 URL |
| `--all` | 重置所有缓存 |
| `--force`, `-f` | 跳过确认（与 --all 配合使用） |
| `--unblock` | 取消阻止指定 URL |

**示例:**

```bash
# 重置单个联系人
linkedincat reset --url "https://linkedin.com/in/user"

# 取消阻止
linkedincat reset --url "https://linkedin.com/in/user" --unblock

# 重置所有（需要确认）
linkedincat reset --all

# 强制重置所有（跳过确认）
linkedincat reset --all --force
```

**警告:** `--all --force` 是危险操作，会清除所有历史记录！

---

## export - 导出历史

导出缓存的历史记录。

```bash
linkedincat export OUTPUT [OPTIONS]
```

**参数:**
| 参数 | 说明 |
|------|------|
| `OUTPUT` | 输出文件路径 |

**选项:**
| 选项 | 说明 |
|------|------|
| `--format` | 输出格式: json, csv |
| `--filter` | 筛选状态: all, sent, blocked, cooldown |
| `--cache-dir` | 缓存目录路径 |

**示例:**

```bash
# 导出为 JSON
linkedincat export history.json

# 导出为 CSV
linkedincat export history.csv --format csv

# 只导出已发送的
linkedincat export sent.json --filter sent

# 只导出被阻止的
linkedincat export blocked.json --filter blocked
```

**JSON 输出格式:**

```json
[
  {
    "url": "https://linkedin.com/in/user-1",
    "timestamp": "2024-01-15T10:30:00",
    "success": true,
    "metadata": {"template": "intro_v1"}
  },
  {
    "url": "https://linkedin.com/in/user-2",
    "timestamp": "2024-01-15T10:32:00",
    "blocked": true,
    "reason": "User declined"
  }
]
```

---

## version - 版本信息

显示当前版本。

```bash
linkedincat version
```

**输出:**

```
🐱 LinkedIn Cat v1.0.0
```

---

## 命令组合示例

### 完整工作流

```bash
# 1. 初始化项目
linkedincat init --path ./linkedin_campaign

# 2. 切换到项目目录
cd ./linkedin_campaign

# 3. 准备 cookies 和 URL 文件
# (手动放置 cookies.json 和编辑 urls/targets.txt)

# 4. 先干运行查看效果
linkedincat send cookies.json message/default.txt urls/targets.txt --dry-run

# 5. 实际发送（无头模式）
linkedincat send cookies.json message/default.txt urls/targets.txt --headless --max 30

# 6. 查看结果
linkedincat status --stats

# 7. 导出记录
linkedincat export results/history.json
```

### 日常使用

```bash
# 早上：检查状态
linkedincat status --stats

# 发送新批次
linkedincat send cookies.json message/intro.txt urls/batch_monday.txt --max 30

# 下午：再发一批
linkedincat send cookies.json message/intro.txt urls/batch_monday.txt --max 20

# 晚上：导出今日记录
linkedincat export "reports/$(date +%Y%m%d).json"
```

---

## 退出码

| 退出码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1 | 一般错误 |
| 2 | 参数错误 |
| 3 | 文件不存在 |
| 4 | cookies 无效 |
| 5 | 达到发送限制 |

---

## 环境变量

CLI 支持以下环境变量：

```bash
# 默认配置文件路径
export LINKEDINCAT_CONFIG="./config.yaml"

# 默认缓存目录
export LINKEDINCAT_CACHE_DIR="./cache"

# 默认无头模式
export LINKEDINCAT_HEADLESS="true"

# 每日限制
export LINKEDINCAT_MAX_DAILY="50"
```
