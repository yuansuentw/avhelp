import configparser

#config = configparser.ConfigParser()
config = {}

config['SITES'] = { "jav321" :
    {
        "NAME" : "Jav321",
        "Desc" : "",
        "BASEURL" : "https://tw.jav321.com/",
        "COOKIES" : {"is_from_search_engine":"1", "is_loyal":"1"},

        "VID_IN_URL": {
            "VALID" : True,
            "URL" : "https://tw.jav321.com/video/{formatted_vid}",
            "FORMAT" : "{vid_series}{vid_number:05}",
            "URL_1" : True,
            "ERROR_SOUP": "html body div.row div.col-md-7.col-md-offset-1.col-xs-12 div.panel.panel-info div.panel-heading h3",
            "ERROR_TEXT" : "",
        },

        "SEARCH" : {
            "URL" : "https://tw.jav321.com/search",
            "METHOD" : "POST",
            "POST_CONTENT_KEY" : "sn",
            "GET_PARAM_KEY" : "",
            "GET_PARAM_VALUE_SEPERATOR" : "",
            "RESULT_SOUP" : "",
            "NOT_FOND_ELE" : "div.alert.alert-danger",
            "NOT_FOND_TEXT" : "未找到",
            "ITEM_ELE" : "",
        },

        "RESULT" : {
            "SINGLE_SOUP":"video#vjs_sample_playe",
            "MULTI_SOUP": "div.panel.panel-info",
        },

        "VIDEO_SOUP" : {
            "COVER_ELE" : "",
            "COVER_ELE_IMG_ATTR" : "",
            "COVER_ZOOMIN_ELE" : "",
            "COVER_ZOOMIN_ELE_IMG_ATTR" : "",
            "THUMB_ELE": "",
            "THUMB_ELE_IMG_ATTR": "",
            "THUMB_ZOOMIN_ELE" : "",
            "THUMB_ZOOMIN_ELE_IMG_ATTR" : "",
            "TITLE_ELE" : "",
            "TITLE_ELE_ATTR" : "",
            "ACTRESS_NAME_ELE" : "",
            "ACTRESS_NAME_ELE_ATTR" : "",
            "RUNTIME_ELE" : "",
            "RUNTIME_ELE_ATTR" : "",
            "PUBLISH_DATE_ELE" : "",
            "PUBLISH_DATE_ELE_ATTR" : "",
            "DATA_DATE_ELE" : "",
            "DATA_DATE_ELE_ATTR" : "",
            "PUBLISHER_ELE" : "",
            "PUBLISHER_ELE_ATTR" : "",
        }
    },

    "Javlib" :{"Name" : "Javlib",
    },
    "Javdb" : {"Name" : "Javdb",
    },
    
}

config['CRAWLER'] = {
    "PIC_PATH" : ".",
    "PIC_FILENAME_FORMAT" : "{vid}{actress}{time}{webfilename}",
    "default_site" : "jav321"
}

#, "Javlib", "Jav123", "Javdb"],


"""
with open('example.ini', 'w') as configfile:
    config.write(configfile)"""