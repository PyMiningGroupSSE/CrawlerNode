FROM python:3.7.1-slim

RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak \
    && echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian/ stretch main contrib non-free" >> /etc/apt/sources.list \
    && echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian/ stretch-updates main contrib non-free" >> /etc/apt/sources.list \
    && echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian/ stretch-backports main contrib non-free" >> /etc/apt/sources.list \
    && echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian-security stretch/updates main contrib non-free" >> /etc/apt/sources.list \
    && apt-get update && apt-get install -y --no-install-recommends wget \
    && pip config set global.index-url "https://pypi.tuna.tsinghua.edu.cn/simple" \
    && pip install lxml requests \
    && wget -O node.tar.gz "https://github.com/PyMiningGroupSSE/CrawlerNode/archive/master.tar.gz" \
    && tar -xzf node.tar.gz && mv CrawlerNode-master crawler-node \
    && rm node.tar.gz \
    && apt-get remove --purge -y wget \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["python", "crawler-node/node.py"]