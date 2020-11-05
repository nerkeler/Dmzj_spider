import os
import re
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


# 获取当前漫画总链接文本
def get_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"}
    res = requests.get(url, headers=headers)
    res.encoding = res.apparent_encoding
    if res.status_code == 200:
        return res.text
    else:
        return None


# 爬取所有章节标题、链接
def get_page(html):
    title_list, href_list = [], []

    soups = BeautifulSoup(html, "lxml")
    soups = soups.find(attrs={"class": "list_con_li autoHeight"})

    for soup in soups.select("li a"):
        title_list.insert(0, soup['title'])
        href_list.insert(0, soup['href'])

    return title_list, href_list  # 返回列表


# 判断是否为数字型字符串
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass


# 爬取章节内所有图片
def main_download(name, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        "Referer": url}  # 浏览器标识
    res = requests.get(url, headers=headers)
    html = res.text  # 动态页面，返回js代码
    link = re.findall("function\(p,a,c,k,e,d\).*?split", html)  # 匹配图片代码片段
    """解码js，构造图片真实链接"""
    first_number = link[0].split("'.split")
    first_number = first_number[0].split("||")
    links, second = [], []
    first = ""
    for i in first_number:
        number = i.split("|")
        for num in number:
            try:
                if is_number(num) and len(num) == 4:
                    first = num  # 链接开始四位数数字串
                elif is_number(num) and (len(num) == 5 or len(num) == 6):
                    second.append(int(num))  # 链接中间数字串
                elif is_number(num) and len(num) >= 7:
                    links.append(num)  # 链接末尾数字串

            except:
                pass
    links = sorted(links)  # 由小到大排序
    # 开始下载图片
    for i in links:
        imgs_link = f'https://images.dmzj.com/img/chapterpic/{first}/{second[0]}/{i}.jpg'  # 构造真实链接

        response = requests.get(url=imgs_link, headers=headers)
        try:
            with open(f"镖人/{name}/{i}.jpg", 'wb') as f:
                f.write(response.content)
        except:
            pass
    print(f"{name}: 已经下载完成")


# 主循环
def main():
    if not os.path.exists("镖人"):  # 创建总文件夹
        os.mkdir("镖人")
    url = "https://www.dmzj.com/info/biaoren.html"
    html = get_url(url)
    title_list, href_list = get_page(html)
    #processing = tqdm(range(0,len(title_list)))
    for name, url in zip(title_list, href_list,):
        if not os.path.exists(f"镖人/{name}"):
            os.mkdir(f"镖人/{name}")
        main_download(name, url)


if __name__ == '__main__':
    main()
