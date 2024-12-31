# Gradient Network 挂机脚本保姆级教程

> 👨‍💻 开发者：小林 (@yoyomyoyoa)

## 🌟 这是什么？

这是一个帮助你自动挂机赚取 Gradient Network 积分的工具。它可以：
- 自动登录账号
- 保持在线状态
- 24小时挂机运行
- 支持代理IP

## 🎯 准备工作

### 1. 注册 Gradient Network 账号
- 点击这里注册：[Gradient Network 注册](https://app.gradient.network/signup?code=VV3TZE)
- 记住你的邮箱和密码，后面需要用到

### 2. 购买代理（强烈推荐）
1. 访问 [Proxy-Cheap](https://app.proxy-cheap.com/r/puD3oz)
2. 注册并登录
3. 选择 Static Residential 类型的代理
4. 购买后，你会得到类似这样的代理地址：
   ```
   socks5://用户名:密码@代理地址:端口
   ```

### 3. 准备服务器
- 推荐使用 Ubuntu 系统的 VPS
- 内存：1GB 及以上
- 建议使用 [Vultr](https://www.vultr.com/) 或 [DigitalOcean](https://www.digitalocean.com/)

## 📝 安装步骤

### 第一步：连接到服务器

#### Windows 用户：
1. 下载并安装 [PuTTY](https://www.putty.org/)
2. 打开 PuTTY
3. 输入你的服务器 IP
4. 点击 "Open"
5. 输入用户名（通常是 root）和密码

#### Mac/Linux 用户：
1. 打开终端
2. 输入：`ssh root@你的服务器IP`
3. 输入密码

### 第二步：安装必要软件

复制以下命令，在服务器终端中运行：
```bash
# 更新系统
apt update && apt upgrade -y

# 安装必要工具
apt install -y curl wget git screen

# 安装 Chrome 依赖
apt install -y fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcairo2 libcups2 libdbus-1-3 libdrm2 libexpat1 libgbm1 libglib2.0-0 libnspr4 libnss3 libpango-1.0-0 libx11-6 libxcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxkbcommon0 libxrandr2 xdg-utils

# 下载并安装 Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 验证安装
google-chrome --version
docker --version
```

### 第三步：下载并运行程序

1. 下载程序：
```bash
# 克隆代码
git clone https://github.com/mumumusf/gradient-network-bot.git
cd gradient-network-bot
```

2. 创建 screen 会话（保证程序不会因为断开 SSH 而停止）：
```bash
screen -S gradient-bot
```

3. 构建并运行 Docker 容器（替换下面的信息为你自己的）：
```bash
# 构建 Docker 镜像
docker build -t gradient-bot .

# 运行容器
docker run -d --name gradient-bot \
-e APP_USER=你的Gradient邮箱 \
-e APP_PASS=你的Gradient密码 \
-e PROXY=socks5://代理用户名:代理密码@代理地址:端口 \
-e DEBUG=true \
--restart always \
gradient-bot
```

4. 查看运行日志：
```bash
docker logs -f gradient-bot
```

5. 按 `Ctrl + A` 然后按 `D` 来保持程序在后台运行

## 🔍 如何检查程序是否正常运行？

1. 重新连接到程序界面：
```bash
screen -r gradient-bot
```

2. 检查运行状态：
```bash
docker ps
```
如果看到 `gradient-bot` 状态是 `Up`，说明程序正在运行

3. 查看最新日志：
```bash
docker logs -f gradient-bot
```

## ❓ 常见问题解答

### 1. 如何判断程序正常运行？
- 日志中显示 "程序已启动！"
- 没有红色的错误信息
- 每30秒会显示一次状态检查信息

### 2. 如何重启程序？
```bash
docker restart gradient-bot
```

### 3. 如何停止程序？
```bash
docker stop gradient-bot
```

### 4. 代理不能用怎么办？
- 确认代理格式是否正确
- 检查代理是否过期
- 尝试更换新的代理

### 5. Chrome 相关错误怎么解决？
- 确保 Chrome 安装成功：`google-chrome --version`
- 如果提示版本不匹配，可以尝试重新安装 Chrome：
  ```bash
  apt remove -y google-chrome-stable
  wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  apt install -y ./google-chrome-stable_current_amd64.deb
  ```

## 📱 需要帮助？

- 开发者：小林
- Twitter：[@yoyomyoyoa](https://twitter.com/yoyomyoyoa)

## ⚠️ 注意事项

1. 请使用可靠的代理服务
2. 定期检查程序运行状态
3. 保持服务器稳定在线
4. 本项目仅供学习交流使用
