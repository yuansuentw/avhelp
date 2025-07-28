from sqlalchemy import MetaData, select, exists,  Column, Integer, String, Time,  create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from nyaadb import NyaaPost, NyaaPostTrends
import urllib.parse
from avtoolsdb import Video
import re
import urllib

url ="https://pixhost.to/show/71/262056981_04feu_fc2ppv-2601867.jpg"

r = requests.get(url) #將此頁面的HTML GET下來
soup = BeautifulSoup(r.text,"html.parser") #將網頁資料以html.parser

i=0
vid ="aa"

for ele in soup.select('img.image-img'):
    img_src = ele.attrs['src'].replace('https','http')
    print(img_src)
    filename = img_src.split("/")[-1]
    urllib.request.urlretrieve(img_src, filename)
    
    #r2 = requests.get(imghref) #將此頁面的HTML GET下來
    ##soup2 = BeautifulSoup(r2.text,"html.parser") 
    #print(soup2)


"""

class JavdbCrawler():
    BASE_URL = 'javdb.com'
    MAXPAGE = 20
    

    def q(self, search_text):
        q = ''
        urls =[]
        
        def qadd(qs):
            nonlocal q
            if len(q) > 0:
                q = q + '&'
            q = q + qs

        if search_text is not None:
            qs =''
            qs += urllib.parse.quote(search_text)
            qadd('f=0&q=' + qs)\
                
        urls.append('http://' + self.BASE_URL + '/search?&f=all&' + qs)

        for url in urls :
            print(url)
            r = requests.get(url) #將此頁面的HTML GET下來
            soup = BeautifulSoup(r.text,"html.parser") #將網頁資料以html.parser

        print(soup)



if __name__ == '__main__':
    a = JavdbCrawler()
    a.q('IPX 762 888')
    """