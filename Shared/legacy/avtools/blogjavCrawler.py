import requests, re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import urllib.parse
from avtools import Video
from utility_ import get_soup, logging_, vid_to_str, convert_time, make_q_url
from urllib.parse import urlparse


def get_videoInfo(series,seriesnumber):
    url, result_count = get_videoUrl_bySearch(series,seriesnumber)
    if url:
        return get_videoInfo_byUrl(url)


def get_videoUrl_bySearch(vid_series, vid_number):

    search_url= make_q_url(base_url="https://blogjav.net/?s={qs}", search_list= (vid_series +' ' + vid_number),saperator="+")
    pageSoup = get_soup(search_url)

    result = pageSoup.select("main.site-main > article")
    result_number = len(result)
    #print("search result total: ",result_number)
    link=None

    if result_number >0:
        for ele in result:
            title = ele.select("header.entry-header > H2 > a")[0].text.strip()
            href = ele.select("header.entry-header > H2 > a")[0].attrs['href']
            # print(vid_series, vid_number,'\n',title,'\n',href)
            if vid_series.upper() in title.upper() and vid_number in title.upper():
                link = href

    return link, result_number


def get_videoInfo_byUrl(videoUrl):
    info = {}
    pageSoup = get_soup(videoUrl)

    title_ele = pageSoup.select("h1.entry-title")
    if len(title_ele) > 0:
        info['title'] = title_ele[0].text.strip()

    info_ele = pageSoup.select(".entry-content > p:nth-child(2)")
    for ele in info_ele[0].children:
        if ele.name is None:
            ele_content = ele.text.strip()
            if ele_content.startswith('タイトル:'):
                ele_v = ele_content[5:].strip()
                ele_key = 'title'
            elif ele_content.startswith('販売日') or ele_content.startswith('発売日') or ele_content.startswith('配信日'):
                ele_v = datetime.strptime(ele_content[3:].strip(), '%Y/%m/%d')
                ele_key = 'pubDate'
            elif ele_content.startswith('再生時間'):
                parsed_time = [a for a in map(int, ele_content[5:].strip().split(':'))]
                if len(parsed_time)== 2:
                    ele_v = convert_time(0, *parsed_time)
                elif len(parsed_time)== 3:
                    ele_v = convert_time(*parsed_time)
                elif len(parsed_time)== 1:
                    ele_v = convert_time(0, *parsed_time,0)
                else:
                    print('無法解析時間格式',ele_content)
                    ele_v = None
                ele_key = 'duration'
            elif ele_content.startswith('出演'):
                ele_v = ele_content[2:].strip()
                ele_key = 'actress_name'
            elif ele_content.startswith('販売者'):
                if info.get('actress_name') is None:
                    ele_v = ele_content[3:].strip()
                    ele_key = 'actress_name'
            else:
                continue

            info[ele_key] = ele_v

    return info


# def get_pic_pixhost(url,path=""):
#     img_src = ""
#     parsed_uri = urlparse(url)
#     if re.match("img\d{1,3}.pixhost.to", parsed_uri.hostname) is not None:
#         get_pic_url(url,path)
#     elif parsed_uri.hostname == "pixhost.to":
#         r = requests.get(url) #將此頁面的HTML GET下來
#         soup = BeautifulSoup(r.text,"html.parser") #將網頁資料以html.parser
#         for ele in soup.select('img.image-img'):
#             img_src = ele.attrs['src'].replace('https','http')
#             filename = img_src.split("/")[-1]
#             filepath = path + filename
#             urllib.request.urlretrieve(img_src, filepath)

#     else:
#         return False


# def get_pic_url(url,path=""):
#     filename = url.split("/")[-1]
#     filepath = path + filename
#     urllib.request.urlretrieve(url.replace('https','http'), filepath)


# def get_pics_byURL(url):
#     r = requests.get(url) #將此頁面的HTML GET下來
#     soup = BeautifulSoup(r.text,"html.parser") #將網頁資料以html.parser

#     for ele in soup.select('div.entry-content img'):
#         #print(ele)
#         parent_name = ele.parent.name
#         imgurl = ""
#         if parent_name == "a":
#             imgurl = ele.parent.attrs['href']
#         elif parent_name == "noscript":
#             pass
#         else:
#             if ele.has_attr('data-lazy-src'):
#                 imgurl = ele.attrs['data-lazy-src']
#             else:
#                 imgurl = ele.attrs['src']


#         if imgurl != "":
#             parsed_uri = urlparse(imgurl)
#             #print(parsed_uri.hostname)
#             if "pixhost" in parsed_uri.hostname :
#                 print("開始抓圖: ",imgurl)
#                 get_pic_url(imgurl)
#             else:
#                 print("不知名的圖床，嘗試直接抓: ",imgurl)
#                 get_pic_url(imgurl)


# def get_pic_search(earch_text):
#     first_link,result_number = search(search_text.strip())
#     if result_number > 0:
#         get_pics_byURL(first_link)
#         return True
#     else:
#         return False


