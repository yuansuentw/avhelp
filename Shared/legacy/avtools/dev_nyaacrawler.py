from sqlalchemy import MetaData, select, exists,  Column, Integer, String, Time,  create_engine, text
from sqlalchemy.orm import declarative_base, session, sessionmaker
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from nyaadb import NyaaPost, NyaaPostTrends
import urllib.parse
from avtoolsdb import Video
from avtools import Avtools
import re




class NyaaTool:
    BASE_URL = 'sukebei.nyaa.si'
    MAXPAGE = 20

    def urlgenerate(self, cat= None, sort= None, order= None, pagenumber= None, search_text= None):
        q = ''  
        
        def qadd(qs):
            nonlocal q
            if len(q) > 0:
                q = q + '&'
            q = q + qs
        
        if cat is not None:
            qadd('c=' + cat.value)

        if sort is not None:
            qadd('s=' + sort.value)

        if order is not None:
            qadd('o=' + order.value)

        if search_text is not None:
            qs =''
            for a in search_text.split(' '):
                if len(qs)>0:
                    qs +='+'
                qs += urllib.parse.quote(a)
            qadd('f=0&q=' + qs)

        url1 = 'https://' + self.BASE_URL + '/?' + q
        urls = [url1]

        
        if pagenumber > self.MAXPAGE:
            pagenumber = self.MAXPAGE

        for i in range(2,pagenumber+1):
            urls.append(url1 + '&p=' + str(i))

        return urls

    def crawlsit(self, cat, sort, order, pagenumber, searchtext=None):
        urls = self.urlgenerate(cat, sort, order, pagenumber,searchtext)
        self.qPostOut24Hr == None

        count=0
        for url in urls :
            print(url)
            r = requests.get(url) #將此頁面的HTML GET下來
            soup = BeautifulSoup(r.text,"html.parser") #將網頁資料以html.parser
        
            for listrow in  soup.select("tbody tr"):
                post, trend = self.trtoobj(listrow)
                print(count, '.  postid:',post.id, ' 【over 24 hr:',self.checklasttrendover24hr(trend), ',  post exist:',self.postexists(post),'】')
                self.updatedb(post,trend)
                count=count+1

    def crawview(self, postdata):
        url = 'https://' + NyaaTool.BASE_URL + '/view/' + str(postdata.id)
        r = requests.get(url) #將此頁面的HTML GET下來
        soup = BeautifulSoup(r.text,"html.parser") #將網頁資料以html.parser
        panel_body = soup.select('div.panel-body div.row')
        submitter = panel_body[1].select('div')[1].text.strip()
        info = panel_body[2].select('div')[1].text.strip()
        hash = panel_body[4].select('div')[1].text.strip()
        return submitter,  info, hash

    def trtoobj(self,listrow):
        tds = listrow.select("td")
        if len(tds) == 8:
            catehref = tds[0].find_all("a")[0]["href"]
            if catehref[:4] == '/?c=':
                cate = catehref[4:]
            #print('cate: '+cate)

            if len(tds[1].findChildren())>1: #有comment
                title = tds[1].find_all("a")[1]["title"].strip()
                href =tds[1].find_all("a")[1]["href"]
                 
            else:
                title = tds[1].a["title"].strip()
                href = tds[1].a["href"]

            if href[:6] == '/view/':
                id = int(href[6:])
            
            #print('id: '+str(id))
            #print('href: '+href)
            #print('title: '+title)

            torrent_url = tds[2].find_all("a")[0]["href"]
            #print('torrent_url:'+torrent_url)

            magnet = tds[2].find_all("a")[1]["href"]
            #print('magnet:'+magnet)

            size =  tds[3].text.strip()
            #print('size:'+size)

            pubdate = tds[4].text.strip()
            #print('date:'+pubdate)

            try:
                seeder = int(tds[5].text)
            except ValueError:
                seeder  = -1
            #print('seeders:'+str(seeders))

            try:
                leacher = int(tds[6].text)
            except ValueError:
                leacher  = -1
            #print('leachers:'+str(leachers))

            try:
                download = int(tds[7].text)
            except ValueError:
                download  = -1
            #print('downloads:'+str(downloads))
            
            grab_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

            vid,series,seriesnumber = self.tool.solvevideoid(title)
            
            post = NyaaPost(id=id,category=cate, title=title, torrent_url=torrent_url,magnet=magnet,size=size, pub_time=pubdate, grab_time=grab_time,  URL=href, videoid=vid)
            if not self.postexists(post):
                post.submitter, post.info, post.hash = self.crawview(post)

            trend = NyaaPostTrends(postid=id, seeder=seeder, leecher=leacher, download=download, data_time=grab_time)

            return post, trend
        else:
            return None

    def updatedb(self,postdata,trenddata):
        added = False
        if not self.postexists(postdata):
            self.session.add(postdata)
            added = True
        if self.checklasttrendover24hr(trenddata):
            self.session.add(trenddata)
            added = True
        if added:
            self.session.commit()

    def postexists(self,postdata): 
        
        if type(postdata) == NyaaPost:
            chk = self.qPost.filter(NyaaPost.id==postdata.id).one_or_none()
        elif type(postdata) == Integer:
            chk = self.qPost.filter(NyaaPost.id==postdata).one_or_none()
        else:
            print('parameter type unexpected!')
            return True
        
        if chk is not None:
            return True
        else:
            return False
    
    def checkString4K(self, str):
        if not hasattr(self,'str4Kre'):
            self.str4Kre = re.compile('4(k|k)|UHD|uhd|2160(P|p)')
        result = self.str4Kre.search(str)
        if result is not None:
            return True
        else:
            return False

    def checklasttrendover1day(self,trend):
        chk = self.qTrend.filter(NyaaPostTrends.postId==trend.postId).order_by(NyaaPostTrends.data_time.desc()).first()
        if chk is None:
            return True
        else:
            return datetime.now()-chk.data_time > timedelta(days=1)

    def checklasttrendover24hr(self,trend):
        if self.qPostOut24Hr is None:
            nowdelta1day = datetime.now()-timedelta(days=1)
            self.qPostOut24Hr = self.qTrend.filter(NyaaPostTrends.data_time > nowdelta1day)

        chk = self.qPostOut24Hr.filter(NyaaPostTrends.postId==trend.postId).first()
        if chk is None:
            return True
        else:
            return False

    
    def postfilter_toVideo(self):


        COMPLETE_DAY = 15
        COMPLETE_DATE_STR = (datetime.now() + timedelta(days=-COMPLETE_DAY)).strftime('%Y-%m-%d')
        COMPLETE_TREASHOULD = 15000
        SEEDER_TREASHOULD = 500
        LEECHER_TREASHOULD = 800
        #x = self.qTrend.join(NyaaPost, NyaaPostTrends.postId == NyaaPost.id).filter(NyaaPostTrends.data_time.between(datetime.today()-timedelta(days=1), datetime.today() ))
        #s = select([NyaaPostTrends.data_time, NyaaPost.title]).select_from(x)
        #print(s)
        #r = self.session.execute(s)
        #for trend in r:
        #    print(trend)

        qs = 'SELECT * FROM (SELECT * From avtools.nyaa_post inner join  \
            (Select postId,seeder,leecher,complete,max(data_time) as data_time  \
            From avtools.nyaa_post_trends group by avtools.nyaa_post_trends.postId ORDER BY data_time Desc) as trend \
            on nyaa_post.id = trend.postId \
            where (avtools.nyaa_post.pub_time > \''+COMPLETE_DATE_STR +'\' and trend.complete > '+str(COMPLETE_TREASHOULD)+')  or trend.seeder> '+str(SEEDER_TREASHOULD)+' or trend.leecher> '+str(LEECHER_TREASHOULD)+') AS nyaa \
            left join avtools.video \
            on nyaa.videoid = video.id \
            where video.isIgnore is null or 0'


        print(qs)
        c = self.session.execute(qs)
        i=0
        for line in c:
            if line.videoid is not None :
                self.tool.addVideoById(videoid=line.videoid, title=line.title)
                print(line.videoid)
            else:
                print(line)
            i+=1
            
        print('total: ',i)




    def __init__(self):

        engine = create_engine('mysql+mysqlconnector://root:ss07k7642-MDB10@192.168.246.168/avtools?charset=utf8mb4&collation=utf8mb4_general_ci')

        

        self.metadata = MetaData(engine)
        Session = sessionmaker()
        Session.configure(bind=engine)
        self.session = Session()
        self.qPost = self.session.query(NyaaPost)
        self.qTrend = self.session.query(NyaaPostTrends)
        self.qPostOut24Hr = None
        pattern ='[0-9]{0,3}[A-Za-z][A-Za-z0-9]{1,4}-\d{2,5}|(FC2|fc2)(-| |)(PPV|ppv|)(-| |)\d{5,7}|STP\d{5}|\d{6}(-|_)\d{3}|(HEYZO|heyzo)(-|_| )\d{3,5}|H4610-[A-Za-z0-9]{5,8}'
        self.videoidregex = re.compile(pattern)
        self.tool = Avtools()
        print("Nyaa crawler init finished...")
