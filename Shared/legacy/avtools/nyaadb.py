from datetime import time
from sqlalchemy import MetaData, Column, Integer, String, Time, DateTime, ForeignKey,  create_engine, text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.types import Enum
import enum
from avtools import Quality
import datetime

Base = declarative_base()


class Cate(enum.Enum):
    ANIME = '1_1'
    Doujinship = '1_2'
    GAMES = '1_3'
    PHOTO = '2_1'
    VIDEO = '2_2'
    MANGA = '1_4'
    PICTURE = '1_5'

class SortMethed(enum.Enum):
    SEEDERS = 'seeders'
    LEECHERS = 'leechers'
    DOWNLOADS = 'downloads'
    DATE = 'id'

class Order(enum.Enum):
    DESC = 'desc'
    ASC = 'asc'

class NyaaPost(Base):
    __tablename__ = 'nyaa_post'
    id  = Column(Integer, primary_key=True)
    category = Column(String(5),Enum(Cate))
    title = Column(String(300))
    torrent_url = Column(String(200))
    magnet = Column(String(5000))
    size = Column(String(15))
    pub_time = Column(DateTime)
    hash = Column(String(40))
    URL = Column(String(200))
    info = Column(String(200))
    submitter  = Column(String(30))
    grab_time = Column(DateTime)
    #trends = relationship("NyaaPostTrends")
    videoid = Column(String(100))
    video_quality = Column(Integer,Enum(Quality))

    def __init__(self, id, category, title, torrent_url,magnet,size, pub_time, grab_time,  URL, hash = None, submitter = None, videoid = None, quality = None):
        self.id = id
        self.category = category
        self.title = title
        self.torrent_url = torrent_url
        self.magnet = magnet
        self.size = size
        self.pub_time = pub_time
        self.hash = hash
        self.URL = URL
        self.submitter = submitter
        self.grab_time = grab_time
        self.video_quality = quality
        self.videoid = videoid

    def __repr__(self):
        return "<NyaaPost('%d','%s')>" % (self.id, self.title)

    def as_dict(self):
       return {c.name: (getattr(self, c.name) if not isinstance(getattr(self, c.name),datetime.datetime) else getattr(self, c.name).strftime('%Y-%m-%dT%H:%M:%S.%f%z')) for c in self.__table__.columns}


class NyaaPostTrends(Base):
    __tablename__ = 'nyaa_post_trends'
    id =  Column(Integer, primary_key=True)
    postId = Column(Integer, ForeignKey('nyaa_post.id'))
    seeder =  Column(Integer)
    leecher =  Column(Integer)
    complete =  Column(Integer)
    data_time = Column(DateTime)

    def __init__(self, postid, seeder, leecher, download, data_time):
        self.postId = postid
        self.seeder = seeder
        self.leecher = leecher
        self.complete = download
        self.data_time = data_time

    def __repr__(self):
        #return "<NyaaPostTrends('%d','%d','%d','%d')>" % (self.id, self.seeder, self.leecher, self.complete)
        return "<NyaaPostTrends('%d','%d','%d','%d','%s')>" % (self.postId, self.seeder, self.leecher, self.complete, self.data_time.strftime("%Y/%m/%d %H:%M:%S"))



if __name__ == '__main__':
    print("GO...")
    engine = create_engine('mysql+mysqlconnector://root:ss07k7642-MDB10@192.168.246.168/avtools?charset=utf8mb4&collation=utf8mb4_general_ci')
    metadata = MetaData(engine)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    Base.metadata.create_all(engine) #// PostTrends.__table__.create(bind=engine, checkfirst=true)
