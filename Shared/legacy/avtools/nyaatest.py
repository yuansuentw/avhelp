from nyaacrawler import NyaaTool
from nyaadb import Cate, SortMethed, Order

a= NyaaTool()

a.crawlsit(Cate.VIDEO, SortMethed.SEEDERS, Order.DESC, 1, '4k')  
a.crawlsit(Cate.VIDEO, SortMethed.DOWNLOADS, Order.DESC,  5)  
a.crawlsit(Cate.VIDEO, SortMethed.SEEDERS, Order.DESC, 3 )  
a.crawlsit(Cate.VIDEO, SortMethed.LEECHERS, Order.DESC, 3)  



a.postfilter_toVideo()
