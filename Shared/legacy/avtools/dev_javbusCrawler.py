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
import logging
from yuansUtility import *



class Javbus():

    def try_vid(self, vid_series, vid_number):
        if len(vid_number)>0:
            vid_number = int(vid_number)
            return  f'{vid_series}-{vid_number:03}'.upper()
        else:
            return vid_series.upper()

    def get_pageSoup(self, url):
        self.logger.debug('q_url: '+url)
        cookies = dict(age_check_done='1', ckcy='2', cklg='ja') #cklg='en' 英語 ，cklg='welcome' 尚未選擇
        r = requests.get(url,cookies=cookies) #將此頁面的HTML GET下來
        soup = BeautifulSoup(r.text,"html.parser") #將網頁資料以html.parser
        return soup

    def get_videoUrl_byTry(self, vid_series, vid_number):
        qs = self.try_vid(vid_series, vid_number)

        try_url =  "https://www.javbus.com/{qs}".format(qs=qs)

        pageSoup = self.get_pageSoup(try_url)
        error404message = pageSoup.select("body > div.container-fluid > div.row > div > h4")
        videoDetail = pageSoup.select("div.container > div.row.movie")
        if len(error404message) ==1:
            if "404 Page Not Found!" in error404message[0].text:
                #print("not found")
                return None
            else:
                print(error404message)
                return None
        elif len(videoDetail) ==1:
            print("found")
            return try_url
        else:
            print("error")
            return None

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

    def get_videoUrl_bySearch(self, vid_series, vid_number):
        if len(vid_number)>0:
            search_text = vid_series + " " + str(vid_number)
        else:
            search_text = vid_series
        base_url="https://www.javbus.com/search/{qs}&type=&parent=ce"
        pageSoup = self.get_pageSoup(self.get_q_url(base_url=base_url, search_text= search_text))

        videou_urls = pageSoup.select("body > div.container-fluid > div.row > div#waterfall > div#waterfall > div.item")
        videoNumber = len(videou_urls)
        resultFoundNothing = pageSoup.select("body > div.container-fluid > div.row > div.alert.alert-danger.alert-page > h4") #搜尋無結果，顯示搜尋提示

        if videoNumber == 1:
            links =  videou_urls[0].select("a")
            if len(links) > 0:
                self.logger.warning("搜尋結果:single")
                return links[0].attrs['href']
            else:
                return None

        elif videoNumber > 1:
            self.logger.warning("搜尋結果:multi")
            if len(vid_series) > 0 and len(vid_number) > 0:
                vid = self.try_vid(vid_series, vid_number)
                #print("vid",vid)
                for v in  videou_urls:
                    link = v.select('a')

                    if len(link)>0:
                        href = link[0].attrs['href']
                        #print(href)
                        if vid in href:
                            return href
            else:
                print("請使用完整vid搜尋")
            return None

        elif len(resultFoundNothing) > 0:
            if "沒有您要的結果！" in resultFoundNothing[0].text :
                self.logger.warning("not found")
            else:
                self.logger.warning("判斷有誤")

            return None
        else:
            self.logger.warning("判斷有誤")
            return None

    def get_video_url(self, vid_series, vid_number):
        javbus_video_url = self.get_videoUrl_byTry(vid_series, vid_number)
        if javbus_video_url is None:
            javbus_video_url = self.get_videoUrl_bySearch(vid_series, vid_number)

        return javbus_video_url



    def get_picsHref_byUrl(self, videoUrl):

        hrefs = []
        soup = self.get_pageSoup(videoUrl)
        bigPic_a = soup.select('html body div.container div.row.movie div.col-md-9.screencap a.bigImage')

        if len(bigPic_a) == 1:
            bigPic_href = "https://www.javbus.com"+ bigPic_a[0].attrs['href']
            hrefs.append(bigPic_href)

        detailPic_a = soup.select('html body div.container div#sample-waterfall a.sample-box')
        for p in detailPic_a:
            hrefs.append(p.attrs['href'])

        return hrefs

    def dl_pic_fromImgUrl(self, url,path=""):
        filename = url.split("/")[-1]
        filepath = path + filename
        print("downloading: ",url)
        opener = urllib.request.build_opener()
        opener.addheaders = [('authority', 'www.javbus.com')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, filepath)

    def dl_pics_byVideoUrl(self, videoUrl):
        picHrefs = self.get_picsHref_byUrl(videoUrl)

        if len(picHrefs) > 0:
            for picHref in picHrefs:
                self.dl_pic_fromImgUrl(picHref)
        else:
            return None

    def dl_pics(self, vid_series, vid_number):
        javbus_url = self.get_video_url(vid_series, vid_number)
        return None if javbus_url is None  else self.dl_pics_byVideoUrl(javbus_url)

    def __init__(self):
        self.logger = getLogger()



if __name__ == '__main__':
    javbus = Javbus()
    javbus.dl_pics("ipx","538")




