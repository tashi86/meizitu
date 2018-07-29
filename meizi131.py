import requests
from lxml import etree
import os
from multiprocessing import Pool

headers = {'Referer': 'http://www.mm131.com/',
            'User-Agent': '''Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 
            (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36'''
           }


# 获取每一页的图集链接地址
# 然后进入每一个图集进行下载相应的图片
# 采用进程池进行多进程任务
def get_page_urls(url):
    re = requests.get(url, headers=headers)
    # 为了防止出现乱码，需要加上encoding,其实为了爬取的可靠性，都应该加上下面的此条语句
    re.encoding = re.apparent_encoding
    html = etree.HTML(re.text)
    urls = html.xpath('//dl[@class="list-left public-box"]//a[@target="_blank"]/@href')
    pool = Pool(processes=4)
    pool.map(parse_page_url, urls)

    # 选择下一页进行翻页
    nextpage = html.xpath('//dd[@class="page"]/a[last()-1]/@href')[0]
    nowpage = html.xpath('//dd[@class="page"]/a[last()-1]/text()')[0]
    if nowpage == '下一页':
        # 采用回调，对下一页进行图片下载
        get_page_urls('http://www.mm131.com/xinggan/' + nextpage)


# 进入详细页面进行图片下载
def parse_page_url(url):
    # 切换到相应的目录，进行图片保存
    os.chdir('E:\\meizi1')
    re = requests.get(url, headers=headers)
    re.encoding = re.apparent_encoding
    html = etree.HTML(re.text)
    src = html.xpath('//div[@class="content-pic"]//img/@src')
    title = html.xpath('//h5/text()')
    # 进入图片详细页面进行采集
    # 部分图片详细页面存在安全警告，出现此种情况就跳过该图集
    if len(src):
        src1 = src[0]
        # 为了简便只选取了图集的前7个字符当作文件夹的名字
        folder = title[0][:7]
        folder_path = os.path.join(os.getcwd(), folder)
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        r = requests.get(src1, headers=headers)
        with open(folder_path + '\\' + src1.split('/')[-1], 'wb') as file:
            file.write(r.content)

        page_now = html.xpath('//div[@class="content-page"]/a[last()]/text()')[0]
        next_page = html.xpath('//div[@class="content-page"]/a[last()]/@href')[0]
        # 采用回调，对下一页进行图片下载
        # 为了防止进入死循环，并有效进行自动翻页，采用了嵌套条件判定
        if next_page:
            if page_now == '下一页':
                parse_page_url('http://www.mm131.com/xinggan/' + next_page)


def main():
    # 起始采集地址
    start_url = 'http://www.mm131.com/xinggan/'
    get_page_urls(start_url)


if __name__ == '__main__':
    main()
