from pydoc import pager
from sqlalchemy import MetaData, select, exists,  Column, Integer, String, Time,  create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from nyaadb import NyaaPost, NyaaPostTrends
import urllib.parse
from avtoolsdb import Video
import re
from urllib.parse import urlparse
import logging
from yuansUtility import *



class DMM():
      
            
    def dl_pic_byUrl(self, url,path=""):
        filename = url.split("/")[-1]
        filepath = path + filename
        urllib.request.urlretrieve(url.replace('https','http'), filepath)


    def get_pic_original_url(self, url):
        """// 画像パスの正規化
        from https://digstatic.dmm.com/js/digital/preview_jquery.js

        function preview_src(src)
        {
            if (src.match(/(p[a-z]\.)jpg/)) {
                return src.replace(RegExp.$1, 'pl.');             xxxxps.jpg => xxxxpl.jpg
            } else if (src.match(/consumer_game/)) {           consumer_gamexxxjs-.jpg => consumer_gamexxx-.jpg
                return src.replace('js-','-'); 
            } else if (src.match(/js\-([0-9]+)\.jpg$/)) {      xxxxjs-18.jpg => xxxxjp-18.jpg
                return src.replace('js-','jp-');
            } else if (src.match(/ts\-([0-9]+)\.jpg$/)) {      xxxxts-18.jpg => xxxxtl-18.jpg
                return src.replace('ts-','tl-');
            } else if (src.match(/(\-[0-9]+\.)jpg$/)) {
                return src.replace(RegExp.$1, 'jp' + RegExp.$1); xxxx-18.jpg => xxxxjp-18.jpg
            } else {
                return src.replace('-','jp-');
            }
        }"""

        re1 = re.compile("(p[a-z]\.)jpg")
        re2 = re.compile("consumer_game")
        re3 = re.compile("js\-([0-9]+)\.jpg$")
        re4 = re.compile("ts\-([0-9]+)\.jpg$")
        re5 = re.compile("(\-[0-9]+\.)jpg$")

        m1 = re1.search(url)
        m2 = re2.search(url)
        m3 = re3.search(url)
        m4 = re4.search(url)
        m5 = re5.search(url)

        if m1 is not None :
            return url.replace(m1.group(1),'pl.')
        elif m2 is not None :
            return url.replace('js-','-')
        elif m3 is not None :
            return url.replace('js-','jp-')
        elif m4 is not None :
            return url.replace('ts-','tl-')
        elif m5 is not None :
            return url.replace(m5.group(1), 'jp' + m5.group(1))
        else:
            return url.replace('-','jp-')

    def dl_pics_byVideoUrl(self, videoUrl):
        picHrefs = self.get_picsHref_byUrl(videoUrl)
        if len(picHrefs) > 0:
            for picHref in picHrefs:
                self.dl_pic_byUrl(picHref)
        else:
            return None

    def get_picsHref_byUrl(self, videoUrl):

        hrefs = []
        soup = self.get_q_pageSoup(videoUrl) 
        bigPic_a = soup.select('div.page-detail div#sample-video > a')
        print(bigPic_a)
        if len(bigPic_a) == 1:
            bigPic_href = bigPic_a[0].attrs['href']
            hrefs.append(bigPic_href)


        detailPic_a = soup.select('div.page-detail div#sample-image-block > a')

        for p in detailPic_a:
            img = p.select('img')
            if len(img) ==1:
                detailPic_href = self.get_pic_original_url(img[0].attrs['src'])
                hrefs.append(detailPic_href)
            
        return hrefs

    def get_q_url(self, base_url ,search_text,saperator = " "):
        qs = ''
        if saperator in [" "]:
            saperator = urllib.parse.quote(saperator)
        if search_text is not None:
            for text in search_text.split(" "):
                coded_text = urllib.parse.quote(text)
                if len(qs)>0:
                    qs+=saperator
                qs+=coded_text
        return base_url.format(qs=qs)
    
    def get_q_pageSoup(self, url):
        self.logger.debug('q_url:'+url)
        cookies = dict(age_check_done='1', ckcy='2', cklg='ja') #cklg='en' 英語 ，cklg='welcome' 尚未選擇
        r = requests.get(url,cookies=cookies) #將此頁面的HTML GET下來
        soup = BeautifulSoup(r.text,"html.parser") #將網頁資料以html.parser
        return soup

  

    def check_pageResult_number(self,pageSoup):
        videou_urls = pageSoup.select("div#main-src > div.d-area > div.d-sect > div.d-item > ul#list > li")
        videoNumber = len(videou_urls)
        resultFoundNothing = pageSoup.select("div#main-src > div.d-area > div.d-sect > div.d-item > div.othertxt > p.red") #搜尋無結果，顯示搜尋提示    
        if videoNumber == 1:
            return "single",videou_urls
        elif videoNumber > 1:
            return "multi",videou_urls
        elif len(resultFoundNothing) > 0:
            if "商品は見つかりません" in resultFoundNothing[0].text :
                return "not found" , None
            else:
                return "unexpect result" , None
        else:
            self.logger.warning("判斷有誤")
            return "unexpect result" , None
            
    def get_video_urls(self, pageSoup):
        resultVideos = pageSoup.select("div#main-src > div.d-area > div.d-sect > div.d-item > ul#list > li")
        a = resultVideos[0].select("a")
        print(a[0].attrs['href'])

    def get_url_bySearch(self, vid_series, vid_number):
        if len(vid_number)>0:
            search_text = vid_series +" "+ str(vid_number)
        else:
            search_text = vid_series
        base_url="https://www.dmm.co.jp/search/=/searchstr={qs}"
        pageSoup = self.get_q_pageSoup(self.get_q_url(base_url=base_url, search_text= search_text))
        pageResultType , video_urls= self.check_pageResult_number(pageSoup)
        
        self.logger.debug(pageResultType)

        if pageResultType == "single":
            links =  video_urls[0].select("a")
            if len(links) > 0:
                return links[0].attrs['href']
            else:
                return None

        elif pageResultType == "multi":
            cid = self.dmmcid(vid_series, vid_number)
            print(cid)
            for v in  video_urls:
                link = v.select('a')
                if len(link)>0:
                    href = link[0].attrs['href']
                    if cid in href:
                        return href
            return None
        else:
            return None
                    

    def dmmcid(self, vid_series, vid_number):
        if len(vid_number)>0:
            vid_number = int(vid_number)
            return  f'{vid_series}{vid_number:05}'.lower()
        else:
            return vid_series

    def get_url_byTry(self, vid_series, vid_number):
        qs = self.dmmcid(vid_series, vid_number)
        
        url =  "https://www.dmm.co.jp/digital/videoa/-/detail/=/cid=1{qs}/".format(qs=qs)
        pageSoup = self.get_q_pageSoup(url)
        error404message = pageSoup.select("h2.d-headline > span.d-txten")
        videoDetail = pageSoup.select("td#mu >div.page-detail")
        if len(error404message) ==1:
            if "404 Not Found" in error404message[0].text:
                print("not found")
                return None
            else:
                print(error404message)
                return None
        elif len(videoDetail) ==1:
            print("found")
            return url
        else:
            print("error")
            return None

    def get_video_url(self, vid_series, vid_number):
        dmm_video_url = self.get_url_byTry(vid_series, vid_number)
        if dmm_video_url is None:
            dmm_video_url = self.get_url_bySearch(vid_series, vid_number)
        return dmm_video_url

    def __init__(self):
        self.logger = getLogger()
        
    def dl_pics(self, vid_series, vid_number):
        dmm_url = self.get_video_url(vid_series, vid_number)

        return None if dmm_url is None  else dmm.dl_pics_byVideoUrl(dmm_url)

    
if __name__ == '__main__':
    #search_text = "fsdss 9999" #not found
    search_text = "fsdss" #single
    #search_text = "fsdss" #multi

    dmm = DMM()
    dmm.dl_pics("fsdss","38")
        
    
    
