# Gradient Network 挂机脚本小白教程

> 👨‍💻 开发者：小林 (@yoyomyoyoa)

## 🌟 这是什么？

这是一个帮助你自动挂机赚取 Gradient Network 积分的工具。它可以帮你：
- 自动登录账号
- 保持在线状态
- 24小时挂机运行
- 支持多账号管理

## 🎯 开始之前你需要准备

1. **必需品**：
   - Gradient Network 账号（[点击注册](https://app.gradient.network/signup?code=EK8G9A)）
   - 一台电脑或服务器（Windows/Mac/Linux 都可以）
   - 稳定的网络环境

2. **可选但推荐**：
   - 代理IP（让你的账号更安全）

## 📝 超简单三步上手

### 第一步：安装 Docker

> Docker 就像一个容器，可以让程序在任何电脑上都能稳定运行

1. 访问 [Docker 官网](https://www.docker.com/get-started/)
2. 下载并安装对应你系统的版本
3. 安装完成后打开终端/命令提示符

### 第二步：选择运行方式

#### 😊 简单版（无代理）
复制下面的命令，替换邮箱和密码后运行：
```bash
docker run -d \
  -e APP_USER=你的Gradient邮箱 \
  -e APP_PASS=你的Gradient密码 \
  overtrue/gradient-bot
```

#### 🚀 进阶版（使用代理）
1. 新建一个文本文件，命名为 `proxies.txt`
2. 在文件中添加你的代理地址，格式如下：
```
socks5://用户名:密码@代理地址:端口
```
3. 运行以下命令：
```bash
docker run -d \
  -e APP_USER=你的Gradient邮箱 \
  -e APP_PASS=你的Gradient密码 \
  -v ./proxies.txt:/app/proxies.txt \
  overtrue/gradient-bot
```

### 第三步：检查是否正常运行

输入以下命令查看运行状态：
```bash
docker ps
```
如果能看到 `overtrue/gradient-bot` 就说明启动成功了！

## 🔍 如何查看运行情况？

1. 先输入 `docker ps` 找到你的容器ID
2. 然后输入：
```bash
docker exec -it 容器ID pm2 logs
```
3. 你就能看到实时运行日志啦！

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
## ⚠️ 温馨提示

1. 请使用稳定的网络环境
2. 定期检查运行状态
3. 建议使用代理IP来提高安全性
4. 本项目仅供学习交流使用

## 🖥️ VPS使用教程

> VPS就是一台远程的电脑，可以24小时运行我们的程序

### 第一步：准备VPS

推荐配置：
- 系统：Ubuntu 20.04/22.04
- 内存：1GB及以上
- 硬盘：20GB及以上
- 推荐服务商：[Vultr](https://www.vultr.com/)、[DigitalOcean](https://www.digitalocean.com/)

### 第二步：连接VPS

1. Windows用户：
   - 下载并安装 [PuTTY](https://www.putty.org/)
   - 输入你的VPS IP地址
   - 输入用户名（通常是root）和密码

2. Mac/Linux用户：
   - 打开终端
   - 输入：`ssh root@你的VPS_IP`
   - 输入密码

### 第三步：安装Docker

复制以下命令到终端运行：
```bash
# 更新系统
apt update && apt upgrade -y

# 安装必要工具
apt install -y curl wget

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 验证Docker安装
docker --version
```

### 第四步：运行脚本

然后按照上面的【运行方式】选择对应的命令运行即可。

#### 💡 VPS使用小贴士：

1. **保持程序运行**
   - 使用 `screen` 或 `tmux` 来保持程序在后台运行
   - 即使你断开SSH连接，程序也会继续运行

2. **基本命令参考**：
```bash
# 创建新的screen会话
screen -S gradient

# 查看所有容器状态
docker ps -a

# 查看容器日志
docker logs 容器ID

# 停止容器
docker stop 容器ID

# 删除容器
docker rm 容器ID
```

3. **安全建议**：
   - 修改默认SSH端口
   - 设置强密码
   - 建议使用SSH密钥登录
   - 开启防火墙

