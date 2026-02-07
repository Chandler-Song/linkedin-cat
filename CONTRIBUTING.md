# Contributing to LinkedIn Cat

感谢您对 LinkedIn Cat 项目的关注！我们欢迎各种形式的贡献。

## 行为准则

请确保您的行为符合开源社区的基本准则：尊重他人、保持专业、友善沟通。

## 如何贡献

### 报告 Bug

1. 在提交 Issue 前，请先搜索是否已有相同问题
2. 使用 Bug 报告模板，提供以下信息：
   - 问题描述
   - 复现步骤
   - 期望行为 vs 实际行为
   - 环境信息（Python 版本、操作系统、浏览器版本等）
   - 相关日志或截图

### 功能建议

1. 清晰描述您希望添加的功能
2. 解释该功能的使用场景
3. 如果可能，提供实现思路

### 提交代码

#### 1. Fork 项目

```bash
# Fork 到您的 GitHub 账户后
git clone https://github.com/YOUR_USERNAME/linkedin_cat.git
cd linkedin_cat
```

#### 2. 创建分支

```bash
# 从 main 分支创建功能分支
git checkout -b feature/your-feature-name

# 或 bug 修复分支
git checkout -b fix/bug-description
```

#### 3. 设置开发环境

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install pytest pytest-cov black flake8
```

#### 4. 编写代码

- 遵循 PEP 8 代码风格
- 为新功能添加测试
- 确保所有测试通过
- 添加必要的文档注释

#### 5. 运行测试

```bash
# 运行所有测试
pytest linkedin_cat/tests/

# 运行带覆盖率的测试
pytest --cov=linkedin_cat linkedin_cat/tests/
```

#### 6. 提交更改

```bash
# 检查代码风格
black linkedin_cat/
flake8 linkedin_cat/

# 提交
git add .
git commit -m "feat: 添加 XX 功能"
```

#### 7. 推送并创建 PR

```bash
git push origin feature/your-feature-name
```

然后在 GitHub 上创建 Pull Request。

## Commit Message 规范

我们采用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Type 类型

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具变更

### 示例

```
feat(message): 添加消息模板变量支持

- 支持 {{firstname}}, {{lastname}}, {{company}} 变量
- 添加默认值语法 {{var|default}}
- 增加变量转义功能

Closes #123
```

## 代码风格

- 使用 4 空格缩进
- 函数和类使用文档字符串
- 变量命名使用 snake_case
- 类名使用 PascalCase
- 常量使用 UPPER_CASE

## 分支命名

- `feature/xxx`: 新功能
- `fix/xxx`: Bug 修复
- `docs/xxx`: 文档更新
- `refactor/xxx`: 代码重构

## Pull Request 检查清单

- [ ] 代码已通过 lint 检查
- [ ] 所有测试已通过
- [ ] 新功能已添加测试
- [ ] 已更新相关文档
- [ ] Commit message 符合规范

## 问题反馈

如有任何问题，请通过 GitHub Issues 联系我们。

再次感谢您的贡献！
