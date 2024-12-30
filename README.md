# Nodepay 自动化工具集

由小林开发的 Nodepay 自动化工具集。
推特: @YOYOMYOYOA

## 功能特点

### 1. Nodepay Bot (bot.py)
- 自动获取账户信息
- 自动完成可用任务
- 每分钟自动发送 Ping
- 支持多账户并行运行
- 灵活的代理配置选项
- IP 评分实时监控

## 安装步骤

### Ubuntu/Debian 系统:
```bash
# 更新系统包
sudo apt update
sudo apt upgrade -y

# 安装必要工具
sudo apt install python3 python3-pip git screen -y

# 克隆代码
git clone https://github.com/mumumusf/nodepay-tools.git
cd nodepay-tools

# 安装依赖
pip3 install -r requirements.txt
```

## 配置说明

### 1. tokens.txt 配置
- 创建 `tokens.txt` 文件
- 每行输入一个 token
- 格式示例：
  ```
  eyJxxxx.yyyy.zzzz
  ```

### 2. 代理配置
三种方式配置代理：
1. **直接输入代理地址**
   - 运行脚本时选择选项 1
   - 支持以下格式：
     ```
     1. ip:port:username:password
     2. ip:port
     3. protocol://ip:port
     4. protocol://username:password@ip:port
     ```

2. **从文件加载代理**
   - 创建代理文件（默认 manual_proxy.txt）
   - 每行一个代理地址

3. **不使用代理**
   - 运行脚本时选择选项 3

## 使用说明

### 在 VPS 上运行（推荐）

1. **创建 screen 会话**
```bash
screen -S nodepay
```

2. **运行脚本**
```bash
python3 bot.py
```

3. **保持脚本后台运行**
- 按 `Ctrl + A`，然后按 `D` 分离 screen 会话
- 脚本会在后台继续运行
- 可以安全地关闭 SSH 连接

4. **查看运行状态**
```bash
# 重新连接到 screen 会话
screen -r nodepay

# 查看日志
tail -f nodepay.log
```

5. **管理 screen 会话**
```bash
# 列出所有会话
screen -ls

# 结束会话
screen -X -S nodepay quit
```

### 本地运行
```bash
python3 bot.py
```

## 日志说明
- 所有操作记录在 `nodepay.log` 文件中
- 包含详细的运行状态和错误信息
- 可以使用 `tail -f nodepay.log` 实时查看

## 获取 Nodepay Token

1. 打开浏览器，登录 Nodepay
2. 按 F12 打开开发者工具
3. 进入 Console 标签
4. 输入以下命令获取 token：
   ```javascript
   localStorage.getItem('np_webapp_token')
   ```
5. 复制获取到的 token 到 tokens.txt 文件

## 注意事项

1. **安全提示**
   - 请勿分享您的 token
   - 建议使用代理以保护账户安全
   - 定期更换代理地址

2. **使用建议**
   - 使用 screen 在 VPS 上运行以确保稳定性
   - 保持网络稳定
   - 使用高质量代理以获得更好的 IP 评分

3. **错误处理**
   - 查看 nodepay.log 文件排查问题
   - 确保网络连接稳定
   - 验证代理可用性

## 问题反馈

如有问题或建议，请通过以下方式联系：
- 推特：@YOYOMYOYOA

## 免责声明

本工具仅供学习和研究使用，使用本工具所产生的任何后果由使用者自行承担。

