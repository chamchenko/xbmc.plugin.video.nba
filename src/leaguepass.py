

from datetime import date
from datetime import timedelta

if sys.version_info.major >= 3:  # Python 3
    from urllib.request import urlopen
    from urllib.error import HTTPError
    from urllib.parse import unquote_plus, urlencode, urlparse, parse_qs
else:  # Python 2
    from urllib2 import Request, urlopen, HTTPError
    from urllib import unquote_plus, urlencode
    from urlparse import urlparse, parse_qs

import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import sys

from utils import *
from games import *
from common import *
from videos import *
from favteam import *
import vars

from tv import TV


def mainMenu():
    addListItem('Live games', 'live', 'live', '', isfolder=True)
    addListItem('Games archive', 'archive', 'archive', '', isfolder=True)
    addListItem('NBA TV', '', 'nba_tv_menu', '', isfolder=True)
    addListItem('Video', '', 'video', '', isfolder=True)
    addListItem('Favorite team\'s games', '', 'favteam', '', isfolder=True)

def archiveMenu():
    addListItem('This week', 'archive', 'thisweek', '', isfolder=True)
    addListItem('Last week', 'archive', 'lastweek', '', isfolder=True)
    addListItem('Select date', 'archive', 'selectdate', '', isfolder=True)

    # Dynamic previous season, so I don't have to update this every time!
    now = date.today()
    is_season_active = False
    is_season_first_year = False
    if now.month >= 10 and date(now.year, 10, 28) < now < date(now.year+1, 6, 30):
        is_season_active = True
        is_season_first_year = True
    elif now.month < 10 and date(now.year-1, 10, 28) < now < date(now.year, 6, 30):
        is_season_active = True

    current_year = now.year
    if is_season_active and not is_season_first_year:
        current_year -= 1

    # Available previous seasons starts from 2012 (2012-1 because range() doesn't include the last year)
    for year in range(current_year-1, 2012-1, -1):
        params = {
            'oldseasonyear': year
        }
        addListItem('%d-%d season' % (year, year + 1), url="", mode='oldseason', iconimage='', isfolder=True, customparams=params)

def liveMenu():
    chooseGameMenu('', 'live')


def previousSeasonMenu():
    season_year = vars.params.get("oldseasonyear")
    season_year = int(season_year)
    start_date = date(season_year, 10, 30)

    # Get the games for 36 weeks
    for week in range(1, 36):
        chooseGameMenu(mode, url, start_date)
        start_date = start_date + timedelta(7)

params = getParams()
url = unquote_plus(params.get("url", ""))
mode = params.get("mode", None)

# Save the params in 'vars' to retrieve it in the functions
vars.params = params;

if mode is None:
    getFanartImage()
    mainMenu()
elif mode == "archive":
    archiveMenu()
elif mode == "playgame":
    play_game()
elif mode == "gamechoosevideo":
    chooseGameVideoMenu()
elif mode == "oldseason":
    previousSeasonMenu()
elif mode == "live":
    liveMenu()
elif mode.startswith("video"):
    if mode == "videoplay":
        videoPlay()
    elif mode == "videolist":
        videoListMenu()
    elif mode == "videodate":
        videoDateMenu()
    else:
        videoMenu()
elif mode == 'nba_tv_menu':
    TV.menu()
elif mode == 'nba_tv_play_live':
    TV.play_live()
elif mode == 'nba_tv_episode_menu':
    TV.episode_menu()
elif mode == 'nba_tv_play_episode':
    TV.play_episode()
elif mode == "favteam":
    if url == "older":
        favTeamOlderMenu()
    else:
        favTeamMenu()
else:
    chooseGameMenu(mode, url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
