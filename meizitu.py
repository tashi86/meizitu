import requests
from bs4 import BeautifulSoup
import time
from multiprocessing import Pool
import os
import re

# 采用两个不同的头部消息
# 头部消息中必须添加referer, 妹子图网站根据referer消息进行反爬虫
Hostreferer = {
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    'Referer': 'http://www.mzitu.com'
               }

Picreferer = {
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    'Referer': 'http://i.meizitu.net'
}


# 采集每一页的图集链接，然后下载图片
def get_image_url(url):
    r = requests.get(url, headers=Hostreferer)
    soup = BeautifulSoup(r.text, 'html.parser')
    items = soup.select('#pins li span a')
    for item in items:
        href = item['href']
        get_image(href)


# 进入详细页面下载整套图集
def get_image(url):
    r = requests.get(url, headers=Hostreferer)
    soup = BeautifulSoup(r.text, 'html.parser')
    name = soup.select('.main-title')[0].get_text()
    # 去除图集名称中不规范的字符
    r_str = r'[/\:*?"<>|：？]'
    name = re.sub(r_str, '', name)

    # 将目录切换到相应的文件夹中
    # 以每套图集的名字建立相应的文件夹
    # 每套图集单独一个文件夹存储
    os.chdir('D:\\python\\meizi')
    filename = os.path.join(os.getcwd(), name)
    if not os.path.exists(filename):
        os.mkdir(filename)

    # 获取每个图集中有多少张图片
    number = int(soup.select('.pagenavi a')[4].string) + 1
    # 观察详细页面每张图片的url地址
    for i in range(1, number):
        if i == 1:
            url1 = url
        else:
            url1 = url + '/' + str(i)
        r1 = requests.get(url1, headers=Hostreferer)
        soup1 = BeautifulSoup(r1.text, 'html.parser')
        # 获取图片地址，并进行保存
        src1 = soup1.select('.main-image img')[0]['src']
        con = requests.get(src1, headers=Picreferer).content
        with open(filename + '\\' + src1.split('/')[-1], 'wb') as f:
            f.write(con)


if __name__ == '__main__':
    urls = ['http://www.mzitu.com/page/{}/'.format(str(i)) for i in range(1, 188)]
    # 采用多进程进行爬取，增加爬取速度
    pool = Pool(processes=4)
    pool.map(get_image_url, urls)
