

import json
import datetime, time
from datetime import timedelta

import xbmc, xbmcplugin, xbmcgui, xbmcaddon
from xml.dom.minidom import parseString
import re

from utils import *
from common import *
import vars
try:
    from urllib.parse import unquote_plus
    from urllib.parse import urlencode
    import urllib.request  as urllib2
except ImportError:
    from urllib import unquote_plus
    from urllib import urlencode
    import urllib2

def videoDateMenu():
    video_tag = vars.params.get("video_tag")

    dates = []
    current_date = datetime.date.today() - timedelta(days=1)
    last_date = current_date - timedelta(days=7)
    while current_date - timedelta(days=1) > last_date:
        dates.append(current_date)
        current_date = current_date - timedelta(days=1)

    for date in dates:
        params = {'date': date, 'video_tag': video_tag}
        addListItem(name=str(date), url='', mode='videolist', iconimage='', isfolder=True, customparams=params)
    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))

def videoMenu():
    url = "https://content-api-prod.nba.com/public/1/endeavor/layout/watch/landing"
    json_parser = json.loads(str(urllib2.urlopen(url).read(), 'utf-8'))
    for category in json_parser['results']['carousels']:
        if category['type'] == "video_carousel":
            addListItem(category['title'], '',
                'videolist', '',True,
                customparams={'video_tag':category['value']['slug'], 'pagination': True})
        elif category['type'] == "collection_cards":
            for collection in category['value']['items']:
                addListItem(collection['name'], '',
                'videolist', '',True,
                customparams={'video_tag':collection['slug'], 'pagination': True})

def videoListMenu():
    xbmcplugin.setContent(int(sys.argv[1]), 'videos')
    date = vars.params.get("date")
    video_tag = vars.params.get("video_tag")
    page = int(vars.params.get("page", 1))
    per_page = 20

    log("videoListMenu: date requested is %s, tag is %s, page is %d" % (date, video_tag, page), xbmc.LOGDEBUG)

    if date:
        selected_date = None
        try:
            selected_date = datetime.datetime.strptime(date, "%Y-%m-%d")
        except:
            selected_date = datetime.datetime.fromtimestamp(time.mktime(time.strptime(date, "%Y-%m-%d")))

    query = []

    base_url = "https://content-api-prod.nba.com/public/1/endeavor/video-list/collection/%s?"
    params = urlencode({
        "sort": "releaseDate desc",
        "page": page,
        "count": per_page
    })

    url = base_url%video_tag + params
    log("videoListMenu: %s: url of date is %s" % (video_tag, url), xbmc.LOGDEBUG)
    response = str(urllib2.urlopen(url).read(), 'utf-8')
    #response = response[response.find("{"):response.rfind("}")+1]
    log("videoListMenu: response: %s" % response, xbmc.LOGDEBUG)
    jsonresponse = json.loads(response)
    for video in jsonresponse['results']['videos']:
        name = video['title']
        release_date = video['releaseDate'].split('T')[0]
        plot = video['description']
        # Runtime formatting
        #minutes, seconds = divmod(video['runtime'], 60)
        #hours, minutes = divmod(minutes, 60)
        runtime = video['program']['runtimeHours']
        thumb = video['image']
        if not date:
            if video['program']['runtimeHours']:
                name = "%s (%s) - %s" % (name, runtime, release_date)
            else:
                name = "%s - %s" % (name, release_date)
        else:
            name = "%s (%s)" % (name, runtime)
        addListItem(url=str(video['program']['id']), name=name, mode='videoplay', iconimage=thumb)
    if vars.params.get("pagination") and page+1 <= jsonresponse['results']['pages']:
        next_page_name = xbmcaddon.Addon().getLocalizedString(50008)

        # Add "next page" link
        custom_params = {
            'video_tag': video_tag,
            'page': page + 1,
            'pagination': True
        }
        if date:
            custom_params['date'] = date

        addListItem(next_page_name, '', 'videolist', '', True, customparams=custom_params)

    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))

def videoPlay():
    video_id = vars.params.get("url")
    if not authenticate():
        return

    url = vars.config['publish_endpoint']
    headers = { 'X-Forworded-For': '103.73.191.10',
        'authorization': 'Bearer %s'%vars.access_token,
        'Content-type': 'application/x-www-form-urlencoded',
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0",
    }
    body = urlencode({
        'id': str(video_id),
        'format': 'json',
        'type': 'video',
    })
    try:
        request = urllib2.Request(url+'?%s'%body, None, headers=headers)
        response = urllib2.urlopen(request, timeout=30)
        content = response.read()
    except urllib2.HTTPError as e:
        logHttpException(e, url, body)
        littleErrorPopup("Failed to get video url. Please check log for details")
        return ''

    json_parser = json.loads(str(content, 'utf-8'))
    video_url = json_parser['path']
    log("videoPlay: video url is %s" % video_url, xbmc.LOGDEBUG)

    # Remove query string
    #video_url = re.sub("\?[^?]+$", "", video_url)

    item = xbmcgui.ListItem(path=video_url)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
