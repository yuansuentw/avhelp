from os import path
import re, urllib, logging, tempfile, pickle, requests, keyboard
from bs4 import BeautifulSoup
from random import randint
from time import sleep
from datetime import time

#TMP_PATH = tempfile.gettempdir() + '/avtools.pickle'
TMP_PATH = path.join(path.dirname(__file__),'tmp')
UHD_SIZE_TREADSHOULD = 15 * 1024 * 1024 *1024 #15GB

def getLogger():
    formatter = logging.Formatter(	'%(asctime)s (%(lineno)d) => %(message)s',	datefmt='%H:%M:%S')
    logger = logging.getLogger('utility')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


logging_ = getLogger()


def make_q_url(base_url ,search_list ,saperator = " "):
    qs = ''
    if saperator in [" "]:
        saperator = urllib.parse.quote(saperator)
    if isinstance(search_list, str):
        search_list = re.split('[ \-,]', search_list)

    for item in search_list:
        coded_text = urllib.parse.quote(item)
        if len(qs)>0:
            qs+=saperator
        qs+=coded_text
    return base_url.format(qs=qs)


def convert_time(hour:int, minute:int, second:int) -> time:
    s = second % 60
    m = (minute + second // 60) % 60
    h = hour + (minute + second // 60) // 60
    return time(h, m, s)


def save_to_pickle(obj, fn):
    if len(fn) > 100:
        fn = fn[:100]
    fn = fn + '.pickle'
    pickle_path = path.join(TMP_PATH, fn)
    if path.exists(pickle_path):
        return None
    else:
        with open(pickle_path, 'wb') as f:
            pickle.dump(obj, f)
            return f


def load_from_pickle(fn):
    if len(fn) > 100:
        fn = fn[:100]
    fn = fn + '.pickle'
    pickle_path = path.join(TMP_PATH, fn)
    if path.exists(pickle_path):
        #logging_.info('load_from_pickle: '+pickle_path)
        with open(pickle_path, 'rb') as f:
            return pickle.load(f)
    else:
        return None


def check_is_4K(fn, fsize):
    str4Kre = re.compile('4(k|k)|UHD|uhd|2160(P|p)')
    result = str4Kre.search(fn)
    if result is not None:
        if fsize >= UHD_SIZE_TREADSHOULD:
            return True

    return False


def url_to_filename(url):
    parsed_url = urllib.parse.urlparse(url)
    if len(parsed_url.scheme) > 0:
        url = url[len(parsed_url.scheme)+3:]

    filename = urllib.parse.quote_plus(url)
    return filename


def check_filename_video(fn):
    VIDEO_FILE_EXTENSIONS = (
        '.264', '.aaf', '.avi', '.divx', '.f4v', '.flv', '.h264', '.kmv', '.m2a', '.m2p', '.m2t', '.m2ts', '.m2v', '.m4e', '.m4u', '.m4v',
        '.mkv', '.mov', '.mp4', '.mpg', '.mpeg', '.mts', '.rm', '.rmv', '.rmvb', '.rts', '.ts','.wmv', '.xmv', '.xvid')
    if fn.endswith((VIDEO_FILE_EXTENSIONS)):
        return True
    else:
        return False


def get_soup(url, cookies=None):
    fn = url_to_filename(url)
    soup = load_from_pickle(fn)
    if not soup:
        logging_.debug('url: '+url)
        sleep(randint(3,5))
        r = requests.get(url, cookies=cookies) #將此頁面的HTML GET下來
        soup = BeautifulSoup(r.text,"html.parser")
        save_to_pickle(soup, fn)
    return soup


def read_key_ny(msg=None):
    if msg:
        print(msg)
        sleep(0.5)
    while True:
        key_pressed = keyboard.read_key()
        if key_pressed in ['Y','y']:
            print(key_pressed)
            sleep(0.5)
            return True
        elif key_pressed in ['N','n']:
            sleep(0.5)
            print(key_pressed)
            return False
        else:
            continue


normal_re = re.compile('[0-9]{0,3}[A-Za-z][A-Za-z0-9]{1,4}-\d{2,5}')
tokyohot_re = re.compile('(th|TH)101|(t|T)okyo(-| )(H|h)ot|東京熱')
tokyohot_number_re = re.compile('((N|n)|(k|K)(a|A|b|B|)|(CZ|cz))\d{4}|(TH101|th101)(-|_)\d{3}(_|-| )\d{6}')
fc2_re = re.compile('(FC2|fc2)(-| |)(PPV|ppv|)(-| |)\d{5,7}')
fc2_number_re = re.compile('\d{5,7}')
h4610_re = re.compile('H4610-[A-Za-z0-9]{5,8}')
heyzo_re = re.compile('(HEYZO|heyzo)(-|_| )\d{3,5}')
heyzo_number_re = re.compile('\d{3,5}')
cari_re = re.compile('\d{6}(-|_)\d{3}')
cari2_re = re.compile('(C|c)(arib|ARIB)|カリビ|加勒比')
ichipon_re = re.compile('1(P|p)on|一本道')
musume_re = re.compile('10(M|m)(U|u)(sume|)')
musume_number_re = re.compile('\d{6}(-|_)\d{2}')
heydouga_re = re.compile('(H|h)(eydouga|EYDOUGA)')
heydouga_number_re = re.compile('\d{4}(-|_)(PPV|ppv|)\d{3,4}')


def solve_vid(title):

    vidString = ''
    idnumber = ''
    idseris = ''

    result = cari_re.search(title)
    if result is not None:
        vidString = result.group()

        result2 = ichipon_re.search(title)
        if result2 is not None:
            idseris = '1Pondo'
            idnumber = vidString.replace('-','_')
        result2 = cari2_re.search(title)

        if result2 is not None:
            idseris = 'Caribbeancom'
            idnumber = vidString.replace('_','-')
        vidString = idseris+'-'+idnumber
        return vidString, idseris, idnumber

    result = fc2_re.search(title)
    if result is not None:
        vidString = result.group()

        result2 = fc2_number_re.search(vidString)
        if result2 is not None:
            idnumber = result2.group()
        else:
            idnumber = ''
        idseris = 'FC2'
        vidString = idseris+'-'+idnumber
        return vidString, idseris, idnumber


    result = musume_re.search(title)
    if result is not None:
        vidString = result.group()
        result2 = musume_number_re.search(title)
        if result2 is not None:
            idnumber = result2.group()
        else:
            idnumber = ''
        idseris = '10musume'
        vidString = idseris+'-'+idnumber
        return vidString, idseris, idnumber

    result = heydouga_re.search(title)
    if result is not None:
        vidString = result.group()
        result2 = heydouga_number_re.search(title)
        if result2 is not None:
            idnumber = result2.group()
        else:
            idnumber = ''
        idseris = 'heydouga'
        vidString = idseris+'-'+idnumber
        return vidString, idseris, idnumber

    result = tokyohot_re.search(title)
    if result is not None:
        vidString = result.group()
        result2 = tokyohot_number_re.search(title)
        if result2 is not None:
            idnumber = result2.group()
        else:
            idnumber = ''
        idseris = 'Tokyo-Hot'
        vidString = idseris+'-'+idnumber
        return vidString, idseris, idnumber

    result = normal_re.search(title)
    if result is not None:
        vidString = result.group()
        tmp = vidString.split('-')
        idseris = tmp[0].upper()
        idnumber = tmp[1]

        vidString = idseris+'-'+idnumber
        return vidString, idseris, idnumber

    result = h4610_re.search(title)
    if result is not None:
        vidString = result.group()
        tmp = vidString.split('-')
        idnumber = tmp[1]
        idseris = 'H4610'
        vidString = idseris+'-'+idnumber
        return vidString, idseris, idnumber

    result = heyzo_re.search(title)
    if result is not None:
        vidString = result.group()
        result2 = heyzo_number_re.search(vidString)
        if result2 is not None:
            idnumber = result2.group()
        else:
            idnumber = ''
        idseris = 'HEYZO'
        vidString = idseris+'-'+idnumber
        return vidString, idseris, idnumber

    return None, None, None


def vid_to_str(vid_series, vid_number):
    if len(vid_number)>0:
        try:
            vid_number = int(vid_number)
        except Exception as e:
            pass
        return  f'{vid_series}-{vid_number:03}'.upper()
    else:
        return vid_series.upper()