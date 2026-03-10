# 📧 AI Email Agent (Gmail 版)

一个基于 Python 的个人智能邮件管家。通过 Gmail IMAP 抓取邮件，利用 LLM 对不同来源的邮件进行多角色（Agent）分类解读与摘要。

---

## 🚀 核心功能

- **多 Agent 路由**：根据转发邮件中的来源（域名/关键词）自动切换不同的 AI 角色（Prompt）和模型。
- **转发识别**：智能从转发邮件正文中提取原始发件人，而非仅仅显示转发者。
- **动态配置**：通过 `.env` 文件或环境变量轻松管理多个 Agent，无需修改代码。
- **每日摘要**：按类别（待办、重要、资讯等）生成 Markdown 格式的每日摘要。

---

## 🛠️ 快速配置

### 1. 准备 Gmail 应用专用密码
1. 登录 [Google 账号管理 - 安全](https://myaccount.google.com/security)。
2. 开启 **两步验证 (2-Step Verification)**。
3. 搜索并进入 **应用专用密码 (App passwords)**。
4. 创建名为 `AI_Agent` 的密码，记下那串 16 位字符（不含空格）。

### 2. 设置配置文件
复制 `.env.example` 为 `.env`：
```bash
cp .env.example .env
```
在 `.env` 中填写你的 `GMAIL_USER` 和 `GMAIL_APP_PASSWORD`。

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

---

## 🤖 如何自定义 Agent 规则

本项目支持通过环境变量**动态定义** Agent。

### Agent 匹配规则
程序会扫描邮件的 **原发件人、收件人别名、正文前 500 字**。如果其中包含你定义的 Agent 名称（不区分大小写），则该 Agent 负责处理。

### 配置示例 (.env)
你可以通过 `EMAIL_AGENT_{NAME}_{KEY}` 的格式定义任意多的 Agent。

```env
# --- Agent 1: 学校邮件 (匹配关键字 'BHAM') ---
EMAIL_AGENT_BHAM_API_KEY=sk-xxxx
EMAIL_AGENT_BHAM_MODEL=gpt-4o
EMAIL_AGENT_BHAM_SYSTEM_PROMPT=你是一位校园助手。这封信来自伯明翰大学，请重点提取 DDL、课程要求和导师指示。

# --- Agent 2: 工作/面试 (匹配关键字 'WORK') ---
EMAIL_AGENT_WORK_API_KEY=sk-yyyy
EMAIL_AGENT_WORK_BASE_URL=https://api.another-llm.com/v1
EMAIL_AGENT_WORK_SYSTEM_PROMPT=你是一位职场专家。请分析这封工作转发邮件，提取行动建议、面试时间或会议摘要。
```

---

## 📝 自定义 Prompt 模板

如果你没有定义特定的 Agent，程序会使用 `default` 配置。

- **默认 Prompt 位置**：`ai_email_agent/llm_processor.py` 中的 `self.system_prompt`。
- **输出摘要位置**：默认在根目录下的 `daily_digest/YYYY-MM-DD.md`。

---

## 🏃 运行项目

```bash
python3 -m ai_email_agent.main
```

## 🧪 运行测试
```bash
python3 -m pytest -q
```
