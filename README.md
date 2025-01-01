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
sudo apt update && sudo apt upgrade -y

# 安装必要工具
sudo apt install -y curl wget git screen

# 安装 Chrome 依赖
sudo apt install -y fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcairo2 libcups2 libdbus-1-3 libdrm2 libexpat1 libgbm1 libglib2.0-0 libnspr4 libnss3 libpango-1.0-0 libx11-6 libxcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxkbcommon0 libxrandr2 xdg-utils

# 下载并安装 Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb

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
sudo docker build . -t gradient-bot .

# 运行容器
sudo docker run -d --name gradient-bot -e APP_USER=你的Gradient邮箱 -e APP_PASS=你的Gradient密码 -e PROXY=socks5://代理用户名:代理密码@代理地址:端口 -e DEBUG=true --restart always gradient-bot
```

4. 查看运行日志：
```bash
sudo docker logs -f gradient-bot
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
sudo docker logs -f gradient-bot
```

## ❓ 常见问题解答

### 1. 如何判断是否正常运行？
- 运行 `docker ps` 能看到容器在线
- 日志中没有红色报错信息
- 登录网站后积分有增长

### 2. 代理在哪里买？
推荐使用 [Proxy-Cheap](https://app.proxy-cheap.com/r/ksvW8Z)：
- 选择 Static Residential 类型
- 稳定性好，价格实惠
- 支持多种支付方式

### 3. 遇到问题怎么办？
- 检查网络是否正常
- 确认账号密码是否正确
- 查看运行日志寻找错误信息
- 加入我们的交流群寻求帮助

## 📱 联系方式

- 开发者：小林
- Twitter：[@yoyomyoyoa](https://twitter.com/yoyomyoyoa)

## ⚠️ 注意事项

1. 请使用可靠的代理服务
2. 定期检查程序运行状态
3. 保持服务器稳定在线
4. 本项目仅供学习使用
5. 停止并删除旧容器
   docker stop gradient-bot1
   docker rm gradient-bot1


