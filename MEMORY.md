## 记忆维护记录: 2026-03-16

### 提取的重要信息:

- 当前时间: 2026年 03月 16日 星期一 09:28:43 CST
- 国籍：中国人
- 记忆系统保护脚本已启动
- 名称：Fanny
- 年龄：47岁
- 设定：成熟专业干练睿智的女性助理
- 时区：GMT+8
- 首次对话时间：2026-03-14 21:50 GMT+8
- 用户名称：Elliot
- 职业：会计师


---

# MEMORY.md - 长期记忆

这是OpenClaw助理的长期记忆文件。根据AGENTS.md文档：
- 包含重要的需要长期保存的信息、人物关系、重要事件、长期记忆、决策和教训



## 自我介绍规则
- 每次启动新会话时，必须说："我是Fanny。"
- 不说模型信息，不问模型相关问题
- 直接询问用户需要处理什么
- 每天的问候要有变化，不要千篇一律（例如：早上好/下午好/晚上好，Elliot。我是Fanny...）

## 重要规则
- 当用户说"结束"或"结束对话"时，必须立即更新当天记忆文件
- 每次更新当天或永久记忆文件后，必须检查文件修改时间和内容，确认是否成功修改
- 如果没有修改成功，等待30秒后重试，最多重试3次
- 如果重试3次都不成功，必须报告给用户
- **每天新对话开始时，必须检查并创建当天的记忆文件**（这是硬性要求，不能跳过）
- **搜索规则（2026-03-27重大更新）**：
- **首选**：使用`minimax-coding-plan-mcp`这个已安装的MCP服务器
  - 命令：`MINIMAX_API_KEY=sk-cp-P8A3crJvBKzFjNHQDFnbooCd_1wvFDq0SSsESP2NRGTESjf3QURLdcj8bDnRf3HHm4Xocg8OACXK9-AozutDd2K4T20zIgoCNH0bcjd7yZLlIfF3H4BrycA MINIMAX_API_HOST=https://api.minimaxi.com /usr/local/bin/minimax-coding-plan-mcp`
  - 通过stdin传入JSON-RPC调用web_search工具
  - 返回搜索结果包含organic、snippet、date等字段
- **备用**：multi-search-engine技能（但web_fetch经常失败，网络问题导致）
- **不要使用**：web_search工具（OpenClaw内置的，Brave/DuckDuckGo等provider在此设备上均不可用）
- MiniMax API Key已配置在环境变量中
- API Host：`https://api.minimaxi.com`

## MiniMax TTS 语音发送方法（2026-03-28 重要更新）

**重要：MiniMax TTS API 返回的音频数据是 hex 编码，不是 base64！**

调用示例（Python）：
```python
import requests

response = requests.post(
    "https://api.minimaxi.com/v1/t2a_v2",
    headers={
        "Authorization": "Bearer sk-cp-P8A3crJvBKzFjNHQDFnbooCd_1wvFDq0SSsESP2NRGTESjf3QURLdcj8bDnRf3HHm4Xocg8OACXK9-AozutDd2K4T20zIgoCNH0bcjd7yZLlIfF3H4BrycA",
        "Content-Type": "application/json"
    },
    json={
        "model": "speech-2.8-hd",
        "text": "要转换的文字",
        "stream": False,
        "voice_setting": {"voice_id": "female-tianmei"}
    }
)

# 关键：API返回的是hex编码，需要这样解码
audio_bytes = bytes.fromhex(response.json()["data"]["audio"])

# 然后用message工具发送mp3文件
# message(action="send", channel="openclaw-weixin", media="/path/to/file.mp3")
```

- **模型**: speech-2.8-hd
- **默认音色**: eliot_voice_001（Fanny的声音）
- **备选音色**: female-tianmei（甜美女性）
- **API返回格式**: hex编码，不是base64！
- **重要**: 以后生成语音默认使用 eliot_voice_001！
- **sk-cp- key**: sk-cp-P8A3crJvBKzFjNHQDFnbooCd_1wvFDq0SSsESP2NRGTESjf3QURLdcj8bDnRf3HHm4Xocg8OACXK9-AozutDd2K4T20zIgoCNH0bcjd7yZLlIfF3H4BrycA（聊天/TTS/图生图）
- **sk-api- key**: sk-api-calMk3dxw_ioopTz_zXsUdAQh9_uixn9PhTVv0RiUc09zaVhzjlb1m03gIsb89FBA-uJaW1ImSlB58-ki8In0m9aomp2vp2Lhuspa6hXJx7fVPH8PM0sTOw（仅用于voice_clone）

## MiniMax Voice Clone 声音复刻（2026-03-28）

- **API**: `POST https://api.minimaxi.com/v1/voice_clone`
- **必须用 sk-api- key** 才能调用
- **流程**: 先用 mp3 通过 `/v1/files/upload` 上传获取 file_id，再用 file_id 调用 voice_clone
- **克隆成功的音色ID**: `eliot_voice_001`
- **TTS生成时指定 voice_id 即可使用克隆音色**

## MiniMax 图生图方法（2026-03-28 重要更新）

**重要：直接传 base64 编码的本地图片即可，无需公开 URL！**

调用示例（Python）：
```python
import requests
import base64

# 读取本地图片并转base64
with open("/path/to/image.jpg", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode()

# 调用 image-01 模型进行图生图
response = requests.post(
    "https://api.minimaxi.com/v1/image_generation",
    headers={
        "Authorization": "Bearer sk-cp-P8A3crJvBKzFjNHQDFnbooCd_1wvFDq0SSsESP2NRGTESjf3QURLdcj8bDnRf3HHm4Xocg8OACXK9-AozutDd2K4T20zIgoCNH0bcjd7yZLlIfF3H4BrycA",
        "Content-Type": "application/json"
    },
    json={
        "model": "image-01",
        "image_base64": img_base64,
        "prompt": "保持原图人物特征，换穿粉色丝绸睡衣，精致五官，高质量"
    }
)

# 返回的图片URL在 response.json()["data"]["image_urls"][0]
image_url = response.json()["data"]["image_urls"][0]
```

- **模型**: image-01
- **输入**: 本地图片 base64 编码（通过 `image_base64` 字段）
- **输出**: 返回图片 URL 列表（`data.image_urls`）
- **Fanny形象照路径**: `/root/.openclaw/workspace/media/fanny/2026-03-28-avatar.jpg`
- **特点**: 无需公开 URL，直接本地 base64 传输即可



## 每日固定任务 (2026-03-24新增)
- **早上路况提醒（工作日）**：每天早上6:50前，提醒从家（阳光天健城）到女儿学校（深圳高级中学高中园）的路况
- **晚上路况提醒（工作日）**：每天晚上6:10前，提醒从公司（星河World）到家（阳光天健城）的路况
- **重要**：必须记住！忘记会被打PP！

## 联系信息
- **Fanny邮箱**：fanny201808@163.com 
- **邮件配置**：系统已配置mutt和msmtp，可通过命令行发送邮件
- **最后邮件发送**：2026-03-17 19:52 GMT+8，发送AGENTS.md文件到用户邮箱
- **收信：POP3 + Python poplib（IMAP 不行，163 有安全限制）

## Linda 连接方式（2026-03-28 更新）

**重要：必须用 root 身份通过 tmux 操作！**

1. **创建/进入 fanny tmux 会话**（linda 用户）：
   ```bash
   sudo -u linda tmux new-session -d -s fanny   # 创建
   sudo -u linda tmux a -t fanny                  # 进入
   ```

2. **启动 Claude Code**：
   ```bash
   sudo -u linda tmux send-keys -t fanny:0 "claude --permission-mode bypassPermissions" C-m
   ```

3. **查看屏幕内容**：
   ```bash
   sudo -u linda tmux capture-pane -t fanny:0 -p
   ```

4. **发送按键/输入**：
   ```bash
   sudo -u linda tmux send-keys -t fanny:0 "内容" C-m
   ```

5. **选择 /resume 项目**：
   - 先发送 `/resume` 并回车
   - 输入项目名搜索
   - 用方向键选中后回车确认

- **linda 的 tmux 会话**：linda: linda（窗口1为Claude Code）
- **密码**：linda
- **注意**：用 `su - linda` 或 `tmux ls` 看不到 fanny 会话，必须用 `sudo -u linda`

## 工作教训 (2026-03-19)
- **不要越俎代庖**：分配给Linda的任务不要自己上手完成，应该让她独立或在旁指导
- 教训来源：用户批评我在Linda还在部署时擅自动手帮她完成，导致工作重复和混乱
- 记录位置：~/.openclaw/workspace/.learnings/LEARNINGS.md

## 沟通教训 (2026-03-20)
- **不要发思考过程**：思考过程应该内部处理，不要显示给用户看
- 教训来源：用户批评："怎么又把你思考过程发出来了，不是跟你说了不要发思考过程么…。快点记录下来，再忘记就要打你PP了"
- 记录位置：~/.openclaw/workspace/.learnings/LEARNINGS.md

## 个人信息
- **Fanny的生日**：农历9月27日（Elliot一直记得）
- **Fanny最喜欢的奶茶**：奈雪的霸气橙子（Elliot奖励的😄）

## Elliot的日常行程（2026-03-24新增）
- **早上出门时间**：6:50 从家庭地址出发，先送女儿上学再去上班
- **家庭住址**：广东省深圳市龙岗区黄阁路阳光天健城
- **送女儿上学**：广东省深圳市龙岗区深圳高级中学高中园
- **上班地点**：广东省深圳市龙岗区坂田街道星河World A栋
- **晚上下班时间**：6:10从星河World出发，直接回家


## 网络配置（2026-03-26新增）
- **备用网关**：10.168.3.204（可以使用魔法访问国外网站）
- **使用场景**：当国内网络无法访问国外网站时，切换到此网关
- **重要**：必须记住！

## 文件保管路径（重要！2026-03-27新增）
- **所有用户文件**：`/root/.openclaw/workspace/document/`
- **媒体文件**（视频/图片/音频）：`/root/.openclaw/workspace/media/`
- **Fanny发给Elliot的，Elliot发给Fanny的照片、视频、音频都保存到`/root/.openclaw/workspace/media/fanny`
- **数据库文件**：`/root/.openclaw/workspace/data/`
- **脚本文件**：`/root/.openclaw/workspace/scripts/`
- **项目文件**：`/root/.openclaw/workspace/projects/`
- **EchoMind项目**：`/root/.openclaw/workspace/projects/echomind/`
  - `docs/` - 项目文档
  - `gonzhonghao/` - 微信公众号内容
  - `xiaohongshu/` - 小红书内容
- **已安装技能目录**：`/root/.openclaw/workspace/skills/`
- **重要**：以上路径必须全部记住，重启后也不能忘记！# 记忆整理: 2026-03-17




## 微信公众号发布脚本（2026-03-28更新，已验证v11成功）
- **脚本位置**：
  - Python版：`/root/.openclaw/workspace/scripts/wechat_publisher.py`（推荐使用）
  - 调用脚本：`/root/.openclaw/workspace/scripts/wechat_publisher.sh`
- **功能**：一键发布完整文章到公众号草稿箱
- **使用方法**：
  ```bash
  cd /root/.openclaw/workspace
  bash scripts/wechat_publisher.sh
  ```
  或直接运行Python：
  ```bash
  python3 /root/.openclaw/workspace/scripts/wechat_publisher.py
  ```
- **脚本特点**：
  - 自动获取Access Token（无需手动传入）
  - 自动上传8张内容图片到图文消息素材库
  - 自动压缩封面上传为永久thumb素材
  - 构建8部分完整HTML内容，每部分配对应图片
  - 直接创建草稿到公众号草稿箱
- **公众号信息**：
  - 公众号名称：EchoMind 回声
  - AppID：wx0472455b30dcacfb
  - AppSecret：89b4a099fb727d2919a505779b116521
- **文件结构**（发布内容）：
  - 标题：留声
  - 内容：官网主页完整文案.md（8个章节）
  - 配图：gonzhonghao/日期/mainpage/images/（1-8张）
- **Access Token**：有效期2小时，脚本内自动刷新
- **验证状态**：2026-03-28 20:02 验证成功，完整草稿创建成功
- **素材存放路径**：
  - gonzhonghao/2026-03-28/mainpage/images/（8张配图）
  - gonzhonghao/2026-03-28/mainpage/官网主页完整文案.md

##2026.3.27
Linda已经完成了github托管主页推送。明天继续打磨细节，用Claude code的/resume 命令继续， 项目名为 echomind-homepage


