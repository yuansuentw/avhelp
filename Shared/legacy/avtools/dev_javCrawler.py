from pydoc import pager
from xmlrpc.client import boolean
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
import os
from  javCrawlerConfig import config


class JavCrawler():

    def __init__(self, config_path=None, log_path=None):
        self.logger = getLogger()
        self.config = config
        self.setSite()


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


    def get_pageSoup(self, url):
        self.logger.debug('get_pageSoup.q_url:'+url)
        cookies = self.SITE_CONFIG['COOKIES']
        response = requests.get(url,cookies=cookies) #將此頁面的HTML GET下來
        soup = BeautifulSoup(response.text,"html.parser") #將網頁資料以html.parser
        return soup, response.url


    def post_pageSoup(self, url, search_text):
        self.logger.debug('post_pageSoup.q_url:'+url)
        cookies = self.SITE_CONFIG['COOKIES']
        self.logger.debug('post_pageSoupq.cookies: '+str(cookies))
        search_key = self.SITE_CONFIG['SEARCH']['POST_CONTENT_KEY']
        data = {search_key:search_text}
        response = requests.post(url,cookies = cookies, data = dict(data))
        soup = BeautifulSoup(response.text,"html.parser") #將網頁資料以html.parser
        return soup, response.url


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
        search_text = vid_series
        if vid_number is not None:
            if type(vid_number) == int:
                vid_number = str(vid_number)
                self.logger.debug('get_url_bySearch.vid_number 是 in type,轉為string: ' + vid_number)
            if len(vid_number)>0:
                search_text = vid_series + " " + vid_number

        self.logger.debug('get_url_bySearch.search_text: '+ search_text)

        search_config = self.SITE_CONFIG['SEARCH']

        search_url = search_config['URL']
        search_method = search_config["METHOD"]


        if search_method =="POST":
            resultSoup, resultUrl = self.post_pageSoup(url=search_url, search_text = search_text)

        elif search_method =="GET":
            q_url = self.search_url(base_url=search_url, search_text= search_text)
            resultSoup, resultUrl = self.get_pageSoup(q_url)

        else:
            self.logger.debug('q_method error, not post nor get: '+ search_method)


        print(resultUrl)
        """
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
                        """

    def result_check(self, result_soup, result_url):
        result_config = self.SITE_CONFIG['RESULT']
        result_SINGLE_SOUP = result_config['SINGLE_SOUP']
        result_MULTI_SOUP = result_config['MULTI_SOUP']

        single_ele = result_soup.select(result_SINGLE_SOUP)
        single_ele_count = len(single_ele)

        multi_ele = result_soup.select(result_MULTI_SOUP)
        multi_ele_count = len(multi_ele)
        self.logger.debug("result_check.single_ele_count: "+str(single_ele_count) +"  result_check.multi_ele_count: " + str(multi_ele_count))

        if single_ele_count == 1 and multi_ele_count <= 1 :
            print('single')
        elif single_ele_count == 0 and multi_ele_count > 1 :
            print('multi')
        else:
            print('error')

    def get_url_byTry(self, vid_series, vid_number):

        if vid_number is None:
            self.logger.debug('請使用完整vid，以便進行網址推測')
            return None

        try_config = self.SITE_CONFIG['VID_IN_URL']

        def check_error(result_soup):
            err_soup = try_config['ERROR_SOUP']
            err_text = try_config['ERROR_TEXT']
            err_ele = result_soup.select(err_soup)
            if len(err_ele) ==1:
                check_text = err_ele[0].text.strip()
                if len(err_text) == 0:
                    if len(check_text) == 0:
                        self.logger.debug('get_url_byTry >嘗試網址失敗: '+url)
                        return True
                else:
                    if err_text in check_text:
                        self.logger.debug('get_url_byTry >嘗試網址失敗: '+url)
                        return True
                return False

        vid_format = try_config['FORMAT']
        formatted_vid = vid_format.format(vid_series=vid_series, vid_number=int(vid_number))
        vid_in_url = try_config['URL']
        url =  vid_in_url.format(formatted_vid=formatted_vid)
        result_soup, result_url = self.get_pageSoup(url)
        err = check_error(result_soup)

        vid_in_url_1 = try_config['URL_1']
        if vid_in_url_1 and err:
            formatted_vid_1 = "1"+formatted_vid
            url1 = vid_in_url.format(formatted_vid=formatted_vid_1)
            self.logger.debug('嘗試1網址: '+url1)
            result_soup, result_url = self.get_pageSoup(url1)
            err = check_error(result_soup)

        if not err:
            return result_soup, result_url
        else:
            return None



        """
else:
            print("get_url_byTry.url.result_url:"+result_url)
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
        """
        return None

    def get_video_url(self, vid_series, vid_number):
        vide_url = None
        is_vid_in_url = self.SITE_CONFIG["VID_IN_URL"]['VALID']
        if is_vid_in_url:
            self.logger.debug('網站支援vid網址表達,開始搜尋.')
            result_soup, result_url = self.get_url_byTry(vid_series, vid_number)
            if result_url is None:
                self.logger.debug('網址表達猜測失敗.')
            else:
                self.logger.debug('get_video_url>網址表達猜測成功,網址是: '+result_url)
                self.result_check(result_soup, result_url)
        if vide_url is None or not is_vid_in_url:
            self.logger.debug('網站不支援vid網址表達,或網址表達猜測失敗,開始搜尋')
            vide_url = self.get_url_bySearch(vid_series, vid_number)
        return vide_url






    def setSite(self, siteName=None):
        default_site = self.config['CRAWLER']['default_site']
        self.logger.debug('預設網站為: '+ default_site )

        if siteName is not None:
            if siteName in self.config['SITES']:
                self.SITE = siteName
                self.SITE_CONFIG = self.config['SITES'][siteName]

                self.logger.debug('指定網站: '+self.SITE )
        else:
            self.SITE = default_site
            self.SITE_CONFIG = config['SITES'][default_site]
            self.logger.debug('使用預設網站: '+default_site)

        self.CRAWLER_CONFIG = config['CRAWLER']

    def dl_pics(self, vid_series, vid_number):
        dmm_url = self.get_video_url(vid_series, vid_number)

        return None if dmm_url is None  else dmm.dl_pics_byVideoUrl(dmm_url)



if __name__ == '__main__':
    #search_text = "fsdss 9999" #not found
    search_text = "STARS-879" #single
    #search_text = "fsdss" #multi
    series = "STARS"
    serirs_number ="879"

    crawler = JavCrawler()
    crawler.get_video_url(series,serirs_number)

