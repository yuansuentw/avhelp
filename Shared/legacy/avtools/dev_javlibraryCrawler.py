
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from nyaadb import NyaaPost, NyaaPostTrends
import urllib.parse
from .avtools import Video
import re
from urllib.parse import urlparse



def get_pageSoup(url):
    r = requests.get(coverFullUrl(url)) #將此頁面的HTML GET下來
    soup = BeautifulSoup(r.text,"html.parser") #將網頁資料以html.parser
    return soup

def try_vid(vid_series, vid_number):
    if len(vid_number)>0:
        vid_number = int(vid_number)
        return  f'{vid_series}-{vid_number:03}'.upper()
    else:
        return vid_series.upper()

def relativeHref_to_absoluteHref(url):
    url = url.replace("tw/","")
    if url[0:2]== "./":
        return "https://www.javlibrary.com/tw" + url[1:]
    elif url[0:1]== "/" and url[1:2] != "/":
        return "https://www.javlibrary.com/tw" + url
    else:
        return url

def coverFullUrl(url):
    if url[0:2]=="//":
        return "https:" + url
    else:
        return url

def solve_picUrl_byPixhostURL(url):
    parsed_uri = urlparse(url)
    if re.match("img\d{1,3}.pixhost.to", parsed_uri.hostname) is not None:
        print("已是完整網址，可直接抓")
        return url
    elif parsed_uri.hostname == "pixhost.to":
        r = requests.get(url) #將此頁面的HTML GET下來
        soup = BeautifulSoup(r.text,"html.parser") #將網頁資料以html.parser
        img = soup.select('img.image-img')
        if len(img) >0:
            return img[0].attrs['src'].replace('https','http')

    else:
        return False

def dl_pic_fromImgUrl(imgUrl,path=""):
    filename = imgUrl.split("/")[-1]
    filepath = path + filename
    parsed_uri = urlparse(imgUrl)

    print('imgUrl:', imgUrl, ', parsed_uri: ',parsed_uri)

    hostname = parsed_uri.netloc

    if hostname is not None:
        if "pixhost" in hostname and re.match("img\d{1,3}.pixhost.to", hostname) is None:
            imgUrl = solve_picUrl_byPixhostURL(imgUrl)

    urllib.request.urlretrieve(imgUrl.replace('https','http'), filepath)

def get_picsHref_byVideoUrl(videoUrl):

    soup = get_pageSoup(videoUrl)
    picUrls = []

    bigPic = soup.select("table#video_jacket_info div#video_jacket > img")

    print("bigPic: "+str(bigPic))
    if len(bigPic) ==1:
        picUrls.append(coverFullUrl(bigPic[0].attrs['src']))
        onErrorCallback = bigPic[0].attrs['onerror']
        if onErrorCallback is not None:
            if onErrorCallback.startswith('JacketError'):
                #onerror="JacketError(this, '//img42.pixhost.to/images/51/147305531_i433776.jpg')"
                #onerror="ImgError(this, 1)"
                altImgSrc = onErrorCallback.replace("JacketError(this,","").replace("')","").replace("'","").strip()
                picUrls.append(coverFullUrl(altImgSrc))

    """
    # 因為小圖真的就只有小圖，所以就取消不抓了
    for ele in soup.select('div.previewthumbs > img'):
        parent_name = ele.parent.name
        imgurl = ""
        if parent_name == "a":
            imgurl = ele.parent.attrs['href']
        elif parent_name == "noscript":
            pass
        else:
            if ele.has_attr('data-lazy-src'):
                imgurl = ele.attrs['data-lazy-src']
            else:
                imgurl = ele.attrs['src']


        if imgurl != "":
            picUrls.append(coverFullUrl(imgurl))
    """

    return picUrls

def get_q_url(base_url ,search_text,saperator = " "):
    qs = ''
    if search_text is not None:
        for text in search_text.split(" "):
            coded_text = urllib.parse.quote(text)
            if len(qs)>0:
                qs+=saperator
            qs+=coded_text
    return base_url.format(qs=qs)

def get_videoUrl_bySearch(self,vid_series, vid_number):
    if len(vid_number)>0:
        search_text = vid_series + " " + str(vid_number)
    else:
        search_text = vid_series

    saperator="+"
    base_url=relativeHref_to_absoluteHref("./vl_searchbyid.php?keyword={qs}")
    searchUrl = get_q_url(base_url=base_url, search_text= search_text,saperator=saperator)
    print(searchUrl)
    pageSoup = get_pageSoup(searchUrl)

    resultSingleTitle = pageSoup.select("div#rightcolumn > div#video_title")
    titleNumber = len(resultSingleTitle)

    resultVideos = pageSoup.select("div#rightcolumn > div.videothumblist > div.videos > div.video")
    videoNumber = len(resultVideos)

    resultFoundNothing = pageSoup.select("div#rightcolumn > div.titlebox > div.boxtitle") #搜尋無結果，顯示搜尋提示

    resultBadSearch = pageSoup.select("div#rightcolumn > div#badalert") #搜尋無結果，顯示搜尋提示，且顯示"搜尋字串是無效的"(ex:全部數字)

    if titleNumber == 1:
        print("單筆資料")
        a = pageSoup.select("html body.main div#content div#rightcolumn div#video_title h3.post-title.text a")
        if len(a)>0:
            href = a[0].attrs['href']
            return relativeHref_to_absoluteHref(href)

    elif videoNumber > 1:
        print("多筆資料: "+str(videoNumber)+ ", title: "+str(titleNumber))
        if len(vid_series) > 0 and len(vid_number) > 0:
            vid = try_vid(vid_series , vid_number)
            for v in resultVideos:
                id =  v.select("div.id")
                if len(id) == 1:
                    a = v.select("a")
                    if len(a) > 0 :
                        href = a[0].attrs['href']
                        if vid in id[0].text:
                            print("found",id[0].text)
                            return_href = relativeHref_to_absoluteHref(href)
            return return_href
        else:
            print("請使用完整vid搜尋")

    elif len(resultFoundNothing)>0:
        if len(resultBadSearch) >0:
            if "字串是無效" in resultBadSearch[0].text :
                print("查詢字串無效")
            else:
                print("判斷例外，檢查程式"+resultBadSearch)
        else:
            if "搜尋提示" in resultFoundNothing[0].text :
                print("查無資料")
            else:
                print("判斷例外，檢查程式"+resultBadSearch)

    else:
        print("判斷例外，檢查程式"+str(titleNumber)+", "+ str(videoNumber))

    return None

def get_videoUrl(self,vid_series, vid_number):
    videoUrl = get_videoUrl_bySearch(vid_series, vid_number)
    return videoUrl

def dl_pics(vid_series, vid_number):
    videoUrl = get_videoUrl(vid_series, vid_number)

    if videoUrl is not None:
        print(videoUrl)
        picsHref = get_picsHref_byVideoUrl(videoUrl)
        print(picsHref)
        if len(picsHref) > 0:
            for picHref in picsHref:
                dl_pic_fromImgUrl(picHref)
            return picsHref
    return None


if __name__ == '__main__':
    javlibrary = Javlibrary()
    javlibrary.dl_pics("IPZZ","046")


