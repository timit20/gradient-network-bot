#!/bin/sh

# 验证 Chrome 是否存在
if [ ! -f "/usr/bin/google-chrome" ]; then
    echo "Chrome not found!"
    exit 1
fi

# 显示 Chrome 版本
google-chrome --version

# 启动应用
pm2 start app.js --name gradient-bot-no-proxy
pm2 logs
