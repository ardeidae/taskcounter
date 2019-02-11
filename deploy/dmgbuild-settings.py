import biplist
import os.path

# dmgbuild -s dmgbuild-settings.py "" ""

application = defines.get('app', 'dist/Taskcounter.app')
appname = os.path.basename(application)
filename = 'Taskcounter.dmg'
volume_name = 'Taskcounter'
format = defines.get('format', 'UDZO')
size = defines.get('size', None)
files = [application]
symlinks = {'Applications': '/Applications'}
badge_icon = 'images/tasks.icns'
icon_locations = {
    appname:        (100, 220),
    'Applications': (325, 220)
}
background = 'images/background.png'
show_status_bar = False
show_tab_view = False
show_toolbar = False
show_pathbar = False
show_sidebar = False
sidebar_width = 180
window_rect = ((100, 100), (450, 480))
default_view = 'icon-view'
arrange_by = None
scroll_position = (0, 0)
label_pos = 'bottom'
text_size = 16
icon_size = 128
