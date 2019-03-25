import requests
import time
import logging
import sys
from urllib.parse import urlparse
from lxml import etree
from conn_client import ClientConnection

__xpath_dict__ = dict()


def main(argv):
    conn = ClientConnection(int(time.time() * 10), argv[1], argv[2])
    conn.connect()

    while True:
        tasks = conn.request_tasks(count=5)
        logging.info("tasks fetch complete, start parsing")
        data_list = list()
        for task in tasks:
            news_type, url = task.split("|")
            host = urlparse(url).netloc
            if host not in __xpath_dict__.keys():
                __xpath_dict__[host] = conn.request_xpath(host)
            data_list.append(parse_page(url, news_type))
            time.sleep(0.5)
        conn.submit_data(data_list)


def parse_page(url, news_type):
    host = urlparse(url).netloc
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8"
    }
    r = requests.get(url, headers=headers)
    if r.status_code not in [200, 404]:
        raise ConnectionError("node might be banned")
    r.encoding = "utf-8"
    selector = etree.HTML(r.text)
    xpath = __xpath_dict__[host]
    article = {
        "url": url,
        "title": None,
        "type": news_type,
        "source": None,
        "time": None,
        "keywords": None,
        "content": ""
    }
    if selector is not None and len(selector.xpath(xpath["title"])) != 0:
        article["title"] = get_value(selector.xpath(xpath["title"]))
        article["source"] = get_value(selector.xpath(xpath["source"]))
        article["time"] = get_value(selector.xpath(xpath["time"]))
        article["keywords"] = selector.xpath(xpath["keywords"])
        content = selector.xpath(xpath["content"])
        for line in content:
            if line.isspace():
                continue
            if line.startswith("\u3000"):
                article["content"] += "\n"
            article["content"] += line.strip()
        article["content"] = article["content"].strip()
    return article


def get_value(selector, index=0):
    if len(selector) == 0:
        return None
    return str(selector[index])


if __name__ == '__main__':
    main(sys.argv)
