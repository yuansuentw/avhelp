import os

from utility_ import solve_vid
from avtools import get_video_by_id
#from .folder_mantain import do_maintain
from javdbCrawler import get_videoInfo, get_videoUrl_bySearch
import blogjavCrawler, folder_mantain

folder_mantain.do_maintain()

# blogjavCrawler.get_videoInfo('Caribbeancom','011324-001')