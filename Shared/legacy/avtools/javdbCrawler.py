import requests, urllib.parse
from datetime import datetime
from utility_ import get_soup, logging_, vid_to_str, convert_time, make_q_url



def get_pageSoup(url):
    #logging_.debug('q_url: '+url)
    return get_soup(url, cookies={'over18':'1', 'theme':'auto', 'locale':'zh','_jdb_session':'5K7WcV5a8aO5mAHCCoLvbLf%2FtGfHWFRdnRDynCLaHHwsVEX%2BRaC7bsEKwGhdTKq17AOesvoZhMwhP%2Ff%2BRsKd%2BCpdTS1WaZtt%2Bat0gb4Y5f7fdh88fGEJxTHwxCQWA0z5TBGAnczvP%2BPbRAWQGEHFCj48cEHForToLNMWEP%2FLWRC2o%2Fw1JiZ2WI5xCATCG7fz5iHgGKdB%2Fun0eYndsXoZM%2BdjRyCtiO4goSvuvqhIC%2Bukery7A17mP9x3gGD%2FW%2BWqcNR5czTQ%2BImETch3oYhhBY5Cihuam9uyHFpzmUbzf0XrEI7WtrPNrF3vDaNBuOLAzstTdhBZ65ipcYbicvrofJtav7Tr4FkVZOrQ%2FqrjN97%2Brz%2Bshmbv57HUaCordKT8weoI93JHOCLc3oH82XEDlWOwphO7ibhC7H0eYmDLSu4zV4x%2BjTAUQL%2BVl7AIZGs1nVblnz7zi4DA8ciH3p5z4o7C--dRVaIXAPdlwfwdf8--8O0IzusjPVYd6g4QQb1GWw%3D%3D'})


def relativeHref_to_absoluteHref(url):
    url = url.replace("tw/","")
    if url[0:2]== "./":
        return "https://javdb.com" + url[1:]
    elif url[0:1]== "/" and url[1:2] != "/":
        return "https://javdb.com" + url
    else:
        return url


def get_videoUrl_bySearch(vid_series, vid_number):

    # if vid_series in ["FC2"]:
    #     return None

    base_url="https://javdb.com/search?q={qs}&f=all"
    search_vid = vid_to_str(vid_series, vid_number)
    search_url = make_q_url(base_url=base_url, search_list= search_vid, saperator='-')
    print(f'search_url for VID: {search_vid} : {search_url}')
    return_href = None
    pageSoup = get_pageSoup(search_url)


    resultVideos = pageSoup.select("div.movie-list div.item")


    videoNumber = len(resultVideos)
    resultFoundNothing = pageSoup.select("div.empty-message") #搜尋無結果，顯示搜尋提示

    if videoNumber == 1:
        links =  resultVideos[0].select("a")
        if len(links) > 0:
            #logging_.warning("搜尋結果:single")
            return links[0].attrs['href']
        else:
            return None

    elif videoNumber > 1:
        found_ = {}
        #logging_.warning("多筆資料: "+str(videoNumber))
        if len(vid_series) > 0 and len(vid_number) > 0:
            vid = vid_to_str(vid_series , vid_number)
            for v in resultVideos:

                # print(v,'#'*80)
                id_eles =  v.select("div.video-title strong")
                date_eles = v.select("div.meta")
                href_eles = v.select("a")
                assert len(id_eles) == 1
                assert len(date_eles) == 1
                assert len(href_eles) == 1

                vid_page = id_eles[0].text.upper()
                date_str = date_eles[0].text.strip()
                date = datetime.strptime(date_str, '%Y-%m-%d')
                href = href_eles[0].attrs['href']



                if vid in vid_page or vid_page in vid:
                    found_[date] = relativeHref_to_absoluteHref(href)

            if len(found_) > 0:
                return_href = found_[max(found_.keys())]
                return return_href

        print("請使用完整vid搜尋")
        return None

    elif len(resultFoundNothing) > 0:
        if "暫無內容" in resultFoundNothing[0].text :
            logging_.warning("not found")
        else:
            logging_.warning("判斷有誤")

        return None
    else:
        logging_.warning("判斷有誤??")
        return None


def get_picsHref_byUrl(videoUrl):

    hrefs = []
    soup = get_pageSoup(videoUrl)
    bigPic_a = soup.select('html.has-navbar-fixed-top.has-navbar-fixed-bottom body section.section div.container div.video-meta-panel div.columns div.column.column-video-cover a.cover-container img.video-cover')

    if len(bigPic_a) == 1:
        bigPic_href = bigPic_a[0].attrs['src']
        hrefs.append(bigPic_href)

    detailPic_a = soup.select('html.has-navbar-fixed-top.has-navbar-fixed-bottom body section.section div.container div.columns div.column article.message.video-panel div.message-body div.tile-images.preview-images a.tile-item')
    for p in detailPic_a:
        hrefs.append(p.attrs['href'])

    return hrefs


def dl_pic_fromImgUrl(url, path=""):
    filename = url.split("/")[-1]
    filepath = path + filename
    print("downloading: ",url)
    opener = urllib.request.build_opener()
    opener.addheaders = [('authority', 'www.Javdb.com')]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, filepath)


def dl_pics_byVideoUrl(videoUrl):
    picHrefs = get_picsHref_byUrl(videoUrl)

    if len(picHrefs) > 0:
        for picHref in picHrefs:
            dl_pic_fromImgUrl(picHref)
    else:
        return None


def dl_pics(vid_series, vid_number):
    Javdb_url = get_videoUrl_bySearch(vid_series, vid_number)
    return None if Javdb_url is None  else dl_pics_byVideoUrl(Javdb_url)


def get_videoInfo_byUrl(videoUrl):
    soup = get_pageSoup(videoUrl)
    info = {}

    check_member_only = soup.select("article.is-warning")

    if len(check_member_only) >0:
        for ele in check_member_only:
            if '此內容需要登入才能查看或操作' in ele.text:
                #logging_.warning("此內容需要登入才能查看或操作")
                return info


    check_vip_only = soup.select("div.message-header")

    if len(check_vip_only) >0:
        for ele in check_vip_only:
            if '需要VIP權限才能訪問此內容' in ele.text:
                #logging_.warning("此內容需要VIP權限")
                return info

    check_vip_only2 = soup.select("h2.title.is-4")

    if len(check_vip_only2) >0:
        for ele in check_vip_only2:
            if '開通VIP' in ele.text:
                #logging_.warning("此內容需要VIP權限")
                return info

    title_ele = soup.select("strong.current-title")

    assert len(title_ele) == 1
    v_title = title_ele[0].text.strip()


    info_eles = soup.select(".movie-panel-info > div.panel-block")
    for info_ele in info_eles:
        #print(info_ele)
        info_key_ele = info_ele.select('div > strong')

        if len(info_key_ele) == 1:
            info_key = info_key_ele[0].text.strip()
            if info_key == "演員:":
                actor_names = []
                eles_a_tag = [ele.text for ele in info_ele.select('div > span.value > a')]
                eles_stront_tag = [ele['class'] for ele in info_ele.select('div > span.value > strong')]
                for actor_name, actor_sex in zip(eles_a_tag, eles_stront_tag):
                    if 'female' in actor_sex:
                        actor_names.append(actor_name)
                        v_title = v_title.replace(actor_name, "")
                info['actress_name'] = ",".join(actor_names)


            elif info_key in ["日期:","時長:"]:
                info_value_ele = info_ele.select('div > span.value')
                info_value = info_value_ele[0].text.strip()

                if info_key == "日期:":
                    info['pubDate'] =  datetime.strptime(info_value, '%Y-%m-%d')
                elif info_key == "時長:":
                    assert info_value[-2:] == "分鍾" #注意不是'分鐘'，鐘字不一樣
                    mins = int(info_value[:-2].strip())
                    info['duration'] = convert_time(0, mins, 0)
            else:
                info_value = None


    info['title'] = v_title.strip()
    splitted_url = videoUrl.split("/")
    assert splitted_url[-2] == 'v'
    info['javdbID'] = splitted_url[-1]

    return info


def get_videoInfo(vid_series, vid_number):
    Javdb_url = get_videoUrl_bySearch(vid_series, vid_number)
    return None if Javdb_url is None  else get_videoInfo_byUrl(Javdb_url)





