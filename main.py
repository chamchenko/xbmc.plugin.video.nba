

import xbmc, xbmcaddon, xbmcvfs
import sys, os


my_addon = xbmcaddon.Addon('plugin.video.nba')
addon_dir = xbmcvfs.translatePath(my_addon.getAddonInfo('path'))

sys.path.append(os.path.join(addon_dir, 'src'))

from leaguepass import *
