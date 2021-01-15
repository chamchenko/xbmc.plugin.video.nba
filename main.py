

from __future__ import unicode_literals

from xbmcvfs import translatePath, exists, mkdir
import xbmcaddon
import sys, os


my_addon = xbmcaddon.Addon('plugin.video.nba')
addon_dir = translatePath(my_addon.getAddonInfo('path'))

sys.path.append(os.path.join(addon_dir, 'src'))

from leaguepass import *
