import os
import time
import datetime
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
requests.packages.urllib3.disable_warnings()


def GetData(page):
    json_dict = {}
    HEADERS = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
               'Accept-Language': 'zh-CN,zh;q=0.8',
               'Accept-Encoding': 'gzip, deflate',
               'Connection': 'close',}
    headers = HEADERS
    headers['user-agent'] = "Mozilla/5.0+(Windows+NT+6.2;+WOW64)+AppleWebKit/537.36+" \
                            "(KHTML,+like+Gecko)+Chrome/45.0.2454.101+Safari/537.36"
    response = requests.get('https://www.zxzxsp.com/page/{}'.format(page),
                            allow_redirects=True,timeout=(30,30),headers=headers,verify=False)
    soup = BeautifulSoup(response.content,'lxml')
    data = soup.find_all('h2')
    for j in data[:-1]:
        url = j.a.get('href')
        t = 0
        while t <3 :
            try:
                response = requests.get(url,allow_redirects=True,timeout=(30,30),headers=headers,verify=False)
                soup = BeautifulSoup(response.content, 'lxml')
                title = soup.h1.string
                div_class = soup.find('div', attrs={'class': 'entry-content u-text-format u-clearfix'})
                if div_class:
                    div = div_class.find_all('img')
                    for img in div:
                        json_dict.update({img.attrs['src']: [div.index(img) + 1, title]})
                else:
                    div_id = soup.find('div', attrs={'id': 'gallery-1'})
                    if div_id:
                        div = div_id.find_all('img')
                        for img in div:
                            json_dict.update({img.attrs['src']: [div.index(img) + 1, title]})
                t = 3
            except requests.exceptions.RequestException as e:
                if t == 2:
                    print(e)
                    print('这期无法访问：{}。'.format(url))
                else:
                    time.sleep(2)
                t += 1

    return json_dict


def GetDownload(json_dict):
    path = os.getcwd()
    HEADERS = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
               'Accept-Language': 'zh-CN,zh;q=0.8',
               'Accept-Encoding': 'gzip, deflate',
               'Connection': 'close', }
    headers = HEADERS
    headers['user-agent'] = "Mozilla/5.0+(Windows+NT+6.2;+WOW64)+AppleWebKit/537.36+" \
                            "(KHTML,+like+Gecko)+Chrome/45.0.2454.101+Safari/537.36"
    for src in json_dict:
        number = json_dict[src][0]
        title = json_dict[src][1]
        mkdirpath = path + '/{}'.format(title)
        os.makedirs(mkdirpath,exist_ok=True)
        t = 0
        while t < 3:
            try:
                img_file = requests.get(src,allow_redirects=True,timeout=(30,30),headers=headers,verify=False)
                if img_file.status_code == 200:
                    img_type = img_file.headers.get('content-type')
                    if img_type.split('/')[-1] == 'jpeg':
                        downPath = mkdirpath + '/{}.jpg'.format(number)
                    else:
                        downPath = mkdirpath + '/{}.{}'.format(number,img_type.split('/')[-1])
                    with open(downPath, 'wb') as f:
                        f.write(img_file.content)
                        t = 3
                else:
                    if t == 2:
                        print('{}第{}张图片无法下载。地址：{}'.format(title,number,src))
                    else:
                        time.sleep(2)
                    t += 1
            except requests.exceptions.RequestException as e:
                if t == 2:
                    print(e)
                    print('{}第{}张图片无法下载。地址：{}'.format(title,number,src))
                else:
                    time.sleep(2)
                t += 1


if __name__ == '__main__':
    print('福利吧-樱桃社下载器\n')
    print('获取和下载需要一定时间，根据您的网速决定，请耐心等待。')
    print('一次性爬取的页数不宜过大，10页以内，防止下载失败。')
    print('窗口有可能卡住，CMD窗口自身原因。您可以按回车键刷新输出。\n')
    start = input("请输入你要从哪一页开始爬取（例：第1页：输入1）\n")
    while start.isdigit() == False or start == '':
        print('请好好输！\n')
        start = input("请输入你要从哪一页开始爬取（例：第1页：输入1）\n")
    end = input("请输入你要从哪一页结束爬取（例：第2页：输入2）\n")
    while end.isdigit() == False or end == '' or end < start:
        print('请好好输！\n')
        end = input("请输入你要从哪一页结束爬取（例：第2页：输入2）\n")
    start = int(start)
    end = int(end) + 1
    starttime = datetime.datetime.now()
    print('获取图片地址，请稍候。。。。。。\n')
    with ThreadPoolExecutor() as executor:
        task_list = []
        json_dict = {}
        for i in range(start,end):
            task = executor.submit(GetData,i)
            task_list.append(task)
        for res in as_completed(task_list):
            json_dict.update(res.result())
    print('图片地址获取完毕，开始下载，请稍候。。。。。。\n')
    with ThreadPoolExecutor() as executor:
        task_list = []
        for key in json_dict:
            task = executor.submit(GetDownload,{key:json_dict[key]})
            task_list.append(task)
        for res in as_completed(task_list):
            res.result()
    endtime = datetime.datetime.now()
    print('已全部下载完成！请在当前路径下查看！用时：{}秒'.format(int((endtime - starttime).total_seconds())))
    print('Enjoy it')
    print('Powered by 所向披靡\n')
    key = input('按c键退出\n')
    while key != 'c':
        key = input('按c键退出\n')