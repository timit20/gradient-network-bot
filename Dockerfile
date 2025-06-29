FROM node:18-slim

# 安装 Chrome 依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    unzip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 安装 Chrome 131.0.6778.69
RUN wget -q -O /tmp/google-chrome-stable_131.0.6778.69-1_amd64.deb \
    https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_131.0.6778.69-1_amd64.deb \
    && apt-get update \
    && apt-get install -y /tmp/google-chrome-stable_131.0.6778.69-1_amd64.deb \
    && rm /tmp/google-chrome-stable_131.0.6778.69-1_amd64.deb \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 验证 Chrome 版本
RUN google-chrome --version

# 安装 PM2
RUN npm install pm2 -g

WORKDIR /app

# 复制项目文件
COPY package*.json ./
RUN npm install
COPY . .

# 设置环境变量
ENV CHROME_PATH=/usr/bin/google-chrome
ENV CHROME_BIN=/usr/bin/google-chrome
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV DISPLAY=:99

# 创建扩展目录
RUN mkdir -p /root/.config/google-chrome/Default/Extensions

# 启动脚本
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]