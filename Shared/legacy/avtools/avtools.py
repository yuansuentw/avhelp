from sqlalchemy.sql.expression import null
from sqlalchemy import Column, Integer,Float, String,Date, Time,DateTime, Boolean, ForeignKey,  create_engine, TEXT
from sqlalchemy.orm import declarative_base,  sessionmaker, validates
from datetime import datetime
import re, enum




Base = declarative_base()

engine = create_engine('sqlite:///avtools.sqlite', echo=False)
Session = sessionmaker(bind=engine)
session = Session()



class Quality(enum.Enum):
    SD = 1
    HD = 2
    FHD = 3
    UHk = 4


"""

class Actress(Base):
    __tablename__ = 'actress'
    id = Column(String(20))
    javdatabaseID
    javdbID
    dmmID
    japaness_name = Column(String(20))
    chinese_name  = Column(String(20))
    english_name   = Column(String(50))
    alias_name = Column(String(200))
    rating
    update
    defaultAction #ask, ignore, download, bytrend

"""


class Video(Base):
    __tablename__ = 'video'
    id = Column(String(60), primary_key=True)
    idSeries = Column(String(30))
    idNumber = Column(String(30))
    dmmID = Column(String(15))
    javdbID = Column(String(20)) #  javdatabase、javlibrary
    pubDate = Column(Date)
    duration = Column(Time)
    title  = Column(String(300))
    actress_name = Column(TEXT)
    actressID = Column(String(20))
    rating = Column(Float)
    #stat #asking, userdownloaded, userignore, autoignore, autodownloaded, trendwatching, trenddownloaded
    isDownloaded = Column(Boolean)
    isIgnore = Column(Boolean)
    addDate = Column(DateTime)
    downloadDate = Column(DateTime)
    deleteDate = Column(Date)
    deleteReason = Column(TEXT)
    remark = Column(TEXT)


    def __init__(self, id,
            idSeries= None, idNumber= None, dmmID= None,javdbID= None, pubDate= None, runtime= None, title = None, actressName = None, actressID = None,
            rating= None, isDownloaded= None, isIgnore= None, addDate= None, downloadDate= None, deleteDate= None, deleteReason= None, remark= None):
        self.id = id
        self.idSeries = idSeries
        self.idNumber = idNumber
        self.dmmID =dmmID
        self.javdbID = javdbID
        self.pubDate = pubDate
        self.runtime = runtime
        self.title  = title
        self.actress_name = actressName
        self.actressID = actressID
        self.rating = rating
        self.isDownloaded = isDownloaded
        self.isIgnore = isIgnore
        self.addDate = addDate
        self.downloadDate = downloadDate
        self.deleteDate = deleteDate
        self.deleteReason = deleteReason
        self.remark = remark


    validate_columns = ['title','actress_name','javdbID','dmmID','id','idSeries','idNumber']

    @validates(*validate_columns)
    def validate_code(self, key, value):
        max_len = getattr(self.__class__, key).prop.columns[0].type.length
        if max_len:
            if value and len(value) > max_len:
                return value[:max_len]
        else:
            #print('field' , key , 'has no max length')
            pass
        return value


    def get_formated_fn(self, is_4k):
        if self.id is None:
            return None

        if self.actress_name:
            if ',' in self.actress_name:
                actress_name = ''
                split_actress_name = self.actress_name.split(',')
                i = 0
                for name in split_actress_name:
                    if i < 3:
                        if len(actress_name) > 0:
                            actress_name += '-'
                        actress_name += name
                    else:
                        actress_name += '等'
                        break
                    i += 1
            else:
                actress_name = self.actress_name

            fn = self.id.upper()
            fn = fn+'_4k' if is_4k else fn
            fn += '_' + actress_name
            return fn
        else:
            return None

    def update_info(self,info_dict):
        if info_dict is not None:
            for key in info_dict:
                if hasattr(self, key):
                    current_value = getattr(self, key)
                    if current_value is None:
                        setattr(self, key, info_dict[key])


    def set_delete(self,reason):
        self.deleteDate = datetime.now()
        self.deleteReason = reason


    def check_basic_info(self):
        check_result = True
        msg_list = []
        if self.id is None:
            msg_list.append('無id')
            check_result = False
        else:
            # FC2等沒有女優名字是正常的
            # if not self.actress_name:
            #     msg_list.append('無女優名字')
            #     check_result = False
            if not self.title:
                msg_list.append('無片名')
                check_result = False


            # print(self.id, ','.join(msg_list))
        return check_result


    def __repr__(self):
        return "<avtoolsdb.Video('%s' , '%s' ,'%s' ,'%s' ,)>" % (self.id,self.title, self.actress_name,self.pubDate)


def get_video_by_id(videoid):
    return session.query(Video).filter(Video.id==videoid).one_or_none()



# if __name__ == '__main__':
#     Base.metadata.create_all(engine) #// PostTrends.__table__.create(bind=engine, checkfirst=true)
#     session.commit()