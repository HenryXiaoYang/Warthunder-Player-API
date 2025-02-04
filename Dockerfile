FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y gnupg2 curl wget unzip ca-certificates xvfb x11vnc xterm x11-xserver-utils libgconf-2-4

# 安装 Chrome WebDriver
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    mkdir -p /opt/chromedriver-$CHROMEDRIVER_VERSION && \
    curl -sS -o /tmp/chromedriver_linux64.zip http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip -qq /tmp/chromedriver_linux64.zip -d /opt/chromedriver-$CHROMEDRIVER_VERSION && \
    rm /tmp/chromedriver_linux64.zip && \
    chmod +x /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver && \
    ln -fs /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver /usr/local/bin/chromedriver

# 安装 Chrome browser
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get -y update && \
    apt-get -y install google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies including pyvirtualdisplay
RUN pip3 install --upgrade pip
RUN pip3 install pyvirtualdisplay

# Copy application files
COPY . .

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Expose the port for the FastAPI server
EXPOSE 5200

# Proxy
ENV http_proxy http://127.0.0.1:7890
ENV https_proxy http://127.0.0.1:7890
ENV HTTP_PROXY http://127.0.0.1:7890
ENV HTTPS_PROXY http://127.0.0.1:7890

# 设置显示环境变量
ENV DISPLAY=:99

# 修改启动命令，使用脚本启动 Xvfb 和应用
COPY start.sh /start.sh
RUN chmod +x /start.sh
CMD ["/start.sh"]