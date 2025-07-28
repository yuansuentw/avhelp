from smb.SMBConnection import SMBConnection
from datetime import datetime, timedelta, UTC
from pathlib import Path
import re
import os
import posixpath, ntpath

from avtools import get_video_by_id, Video, session
from utility_ import solve_vid, check_is_4K, read_key_ny, check_filename_video
import  javdbCrawler, blogjavCrawler


EXCLUDE_PATH = ('.', '..','$RECYCLE.BIN','System Volume Information')
SHARED_NAME = 'video'
CHECK_DATE = True #是否檢查日期，全域設定，會影響自動刪除等
CHECK_WITHTHIN_DAYS = 180
CHECK_FN = True
CHECK_DELETE = True
CHECK_RENAME = True
MOVE_FOLDER = True
MOVE_FOLDER_WINTHIN_DAYS = 60
MAINTAIN_DEPTH = 0

def extract_smb_info(smb_url):
    # 定義正則表達式來匹配所需的部分
    pattern = r'smb://(?P<username>[^:]+):(?P<password>[^@]+)@(?P<host>[^/]+)/(?P<path>.+)'

    match = re.match(pattern, smb_url)
    if match:
        return match.group('username'), match.group('password'), match.group('host'), match.group('path')
    else:
        raise ValueError("URL 格式不正確")


def get_platform_path_separator(path):
    """根據路徑字串判斷路徑分隔符

    Args:
        path (str): 路徑字串

    Returns:
        str: 路徑分隔符
    """
    if "\\" in path:
        return "\\"
    else:
        return "/"

def do_maintain():
    #smb_url = 'smb://Yuan:ss07k7642iris@192.168.246.168/video'
    get_all_files_local('Z:\\video\\Download', current_depth=0, depth_max=MAINTAIN_DEPTH)


def get_all_files(path, conn=None, current_depth=0, depth_max=3):
    #smb://username:password@hos_tname/share_folder
    if path.startswith('smb'):
        username, password, host, path = extract_smb_info(path)
        conn = SMBConnection(username,password,"","",use_ntlm_v2 = True)
        try:
            connected  = conn.connect(host, 445)
            if connected:
                print("登錄成功")
                return conn
        except Exception as e:
            print(str(e))
        return get_all_files_smb(path, current_depth, depth_max, conn)
    else:
        return get_all_files_local(path, current_depth, depth_max)


def get_all_files_smb(currentpath, current_depth=0, depth_max=3, conn=None):
    if current_depth > depth_max:
        return

    response = conn.listPath(SHARED_NAME, currentpath, timeout=30)
    # totalFiles = len(response)

    for f in response:
        fn = f.filename
        if fn in EXCLUDE_PATH:
            continue

        fctime = datetime.fromtimestamp(f.create_time, UTC)
        if f.isDirectory:
            get_all_files_smb(os.path.join(currentpath, fn).replace('\\', '/'), current_depth + 1, depth_max, conn)
        else:
            process_file(currentpath, fn, f, fctime, conn)


def get_all_files_local(currentpath, current_depth=0, depth_max=3):
    if current_depth > depth_max:
        return

    path = Path(currentpath)
    # totalFiles = sum(1 for _ in path.iterdir())

    for f in path.iterdir():
        if f.name in EXCLUDE_PATH:
            continue

        fctime = datetime.fromtimestamp(f.stat().st_ctime)
        if f.is_dir():
            get_all_files_local(str(f), current_depth + 1, depth_max)
        else:
            process_file(str(path), f.name, f, fctime)



def process_file(currentpath, fn, f, fctime, conn=None):

    if not check_filename_video(fn):
        return

    if CHECK_DATE and fctime < (datetime.now() + timedelta(days=-CHECK_WITHTHIN_DAYS)):
        #print(fn,': 超過檢查日期區間，跳過',fctime.strftime("%Y/%m/%d %H:%M:%S"),' < ',(datetime.now() + timedelta(days=-CHECK_WITHTHIN_DAYS)).strftime("%Y/%m/%d %H:%M:%S"))
        return

    vid, series, seriesnumber = solve_vid(fn)
    if not vid:
        print(fn, ': 檔名無法解析')
        return

    entity = get_video_by_id(vid)
    if not entity: #資料庫搜尋不到
        entity = Video(id=vid, idSeries=series, idNumber=seriesnumber)
        entity.addDate = datetime.now()

    if not entity.check_basic_info():
        print(vid,': 資料庫資料不完整，重新抓取')
        entity.downloadDate = fctime
        entity.isDownloaded = True
        entity.isIgnore = True

        if series in ['Tokyo-Hot', 'FC2', 'Caribbeancom']:
            v_info = blogjavCrawler.get_videoInfo(series,seriesnumber)
        else:
            v_info = javdbCrawler.get_videoInfo(series,seriesnumber)

        entity.update_info(v_info)
        if entity.check_basic_info():
            session.add(entity)
            session.commit()
            print(vid,': 新增影片')
        else:
            print(vid,': 嘗試新增影片，但因無法取得相關資訊所以儲存失敗',v_info)
            return


    separator = get_platform_path_separator(currentpath)
    if separator == '\\':
        pathlib = ntpath
    else:
        pathlib = posixpath

    # if MOVE_FOLDER and current_depth ==1 and totalFiles ==3 and fctime > (datetime.now() + timedelta(days=-MOVE_FOLDER_WINTHIN_DAYS)): #totalFiles 包含. 和..
    #     move_path = '\\'.join((currentpath.split('\\'))[:-1])
    # else:
    move_path = currentpath

    new_fn = fn
    if CHECK_DELETE and (fn.startswith('X_') or fn.startswith('x_')) and entity.check_basic_info():
        matched = re.findall('\([-\w\u0800-\u9fa5\uFF00-\uFFFF]+\)', fn)
        if matched:
            assert len(matched) == 1
            reason = matched[0][1:-1]
            if read_key_ny(fn + ' 刪除檔案(Y/N)?:'):
                old_path = pathlib.join(currentpath, fn)
                new_path = pathlib.join(currentpath, 'waiting_delete', fn)
                print(old_path, ' => ', new_path)
                try:
                    if conn:
                        conn.rename('video',old_path,new_path,timeout=30)
                    else:
                        os.rename(old_path, new_path)
                    entity.set_delete(reason)
                    session.commit()
                except Exception as e:
                    print('刪除過程發生錯誤:',e)
                finally:
                    print(' ..成功刪除')
            else:
                print(' ..取消刪除')
    elif CHECK_FN:
        file_size = f.file_size if conn else f.stat().st_size
        formated_fn = entity.get_formated_fn(is_4k=check_is_4K(fn,file_size))
        if formated_fn:
            if formated_fn.upper() not in fn.upper() and CHECK_RENAME:
                new_fn_tmp = formated_fn + Path(fn).suffix
                print(f"更改檔名 {fn} => {new_fn_tmp} (Y/N)?:")
                if read_key_ny():
                    new_fn = new_fn_tmp
                elif 'hhd800.com@' in fn:
                    print(f"更改檔名 {fn} => {fn.replace('hhd800.com@','')} (Y/N)?:")
                    if read_key_ny():
                        new_fn = fn.replace('hhd800.com@','')

    if new_fn != fn or move_path != currentpath:
        msg_list = []
        if new_fn != fn:
            msg_list.append('更改檔名')
        if move_path != currentpath:
            msg_list.append('移動檔案')
        msg = ','.join(msg_list)
        try:
            old_path = pathlib.join(currentpath, fn)
            new_path = pathlib.join(move_path, new_fn)
            if conn:
                conn.rename('video',old_path,new_path,timeout=30)
            else:
                os.rename(old_path, new_path)
            print(f' ..{msg}成功')
        except Exception as e:
            print(f' ..{msg}失敗', e)

        if move_path != currentpath:
            try:
                if conn:
                    conn.deleteDirectory('video', currentpath,timeout=30)
                else:
                    os.rmdir(currentpath)
                print(f' ..刪除資料夾成功:', currentpath)
            except Exception as e:
                print(f' ..刪除資料夾失敗:', currentpath, e)
    #沒有移動檔案或改檔名，才會檢查是否要刪除
