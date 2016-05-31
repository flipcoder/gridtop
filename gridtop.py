#!/usr/bin/env python2

import sys
import subprocess
from copy import copy
import time

if len(sys.argv) <= 1:
    sys.exit(1)

BLACKLIST = [
    'Desktop',
    'nemo',
    'plank',
    'wmctrl -l -G',
    'pcmanfm',
    'x-caja-desktop',
    'Bottom Expanded Edge Panel'
]

# OFFSET = [ 11, 68 ]
# OFFSET = [8, 50]
OFFSET=[2,48]

DELAY = 1.0

SCREEN_W = 1920
SCREEN_H = 1080
GRID_SIZE = 4
BOTTOM_PANEL = 24
NUM_DISPLAYS = 3

# screen edges
SNAP_X = [0,SCREEN_W,SCREEN_W*2,SCREEN_W*3]
SNAP_Y = [0,SCREEN_H-BOTTOM_PANEL]

# grid regions
GRID = [1920 // GRID_SIZE, (1080-BOTTOM_PANEL) // GRID_SIZE]

class Window:
    def __init__(self, name, line):
        self.name = name
        self.num = int(line[0], 16)
        self.desktop = int(line[1])
        self.pos = (int(line[2]), int(line[3]))
        self.size = (int(line[4]), int(line[5]))
        self.active = False
    def get_x(self):
        return self.pos[0]
    def get_y(self):
        return self.pos[1]
    def center_x(self):
        return self.pos[0] + self.size[0] / 2
    def center_y(self):
        return self.pos[1] + self.size[1] / 2
    def activate(self):
        print subprocess.check_output(['wmctrl','-i','-a', str(self.num)]).split('\n')[0]
    def __repr__(self):
        c = (self.center_x(),self.center_y())
        return "%s [%s, %s]%s" % (self.name, c[0], c[1], (" (active)" if self.active else ""))

active_window_num = int(subprocess.check_output(['xdotool','getactivewindow']).split('\n')[0])

def next(d,w):
    for i in range(len(w)):
        if w[i].active:
            return min(max(0,i+d),len(w)-1)
    return None

def active_window_idx(w):
    for i in range(len(w)):
        if w[i].active:
            return i
    return None

def snap(active_window):
    x = active_window.pos[0]
    y = active_window.pos[1]
    x2 = active_window.size[0]
    y2 = active_window.size[1]
    # print x,y,x2,y2
    x2 = int(round((x2+x+GRID[0]/2)//GRID[0])*GRID[0])
    y2 = int(round((y2+y+GRID[1]/2)//GRID[1])*GRID[1])
    x = int(round(x+GRID[0]/2)//GRID[0]*GRID[0])
    y = int(round(y+GRID[1]/2)//GRID[1]*GRID[1])
    # print x,y,x2,y2
    diffx = max(0,int(x)-OFFSET[0]) - (int(x)-OFFSET[0])
    diffy = max(0,int(y)-OFFSET[1]) - (int(y)-OFFSET[1])
    subprocess.call([
        'wmctrl', '-r', ':ACTIVE:', '-e', '0,%s,%s,%s,%s' % (
            max(0,int(x)-OFFSET[0]),
            max(0,int(y)-OFFSET[1]),
            max(GRID[0],x2-x) - diffx,
            max(GRID[1],y2-y) - diffy
        )
    ])

    # just in case we need this updated after the snap call:
    active_window.pos = (x,y)
    active_window.size = (
        max(GRID[0],x2-x) - diffx,
        max(GRID[1],y2-y) - diffy
    )
    
windows = []
active_window = None
def update():
    global windows
    global active_window
    lines = subprocess.check_output(['wmctrl', '-G', '-l']).split('\n')
    lines = lines[:-1]
    active_window = None
    for i in range(len(lines)):
        lines[i] = lines[i].split(' ')
        lines[i] = filter(lambda x: x, lines[i])
        name = ' '.join(lines[i][7:])
        lines[i] = lines[i][:6]
        if name in BLACKLIST and lines[1]=="-1":
            continue
        windows += [Window(name, lines[i])]
        if windows[-1].num == active_window_num:
            active_window = windows[-1]
            windows[-1].active = True
def just_this_desktop():
    global windows
    global active_window
    windows = filter(lambda x: x.desktop == active_window.desktop or x.desktop == "-1", windows)
update()

if sys.argv[1]=="left":
    just_this_desktop()
    all_windows = sorted(windows, cmp=lambda x,y: x.get_x() - y.get_x())
    windows = copy(all_windows)
    windows = sorted(windows, cmp=lambda x,y: x.get_x() - y.get_x())
    active = windows[active_window_idx(windows)]
    windows = filter(lambda x: active.pos[1] + active.size[1] >= x.pos[1], windows)
    windows = filter(lambda x: active.pos[1] <= x.pos[1] + x.size[1], windows)
    windows = filter(lambda x: active == x or active.center_x() != x.center_x(), windows)
    if windows:
        idx = next(-1, windows)
        if idx != None:
            windows[idx].activate()
elif sys.argv[1]=="right":
    just_this_desktop()
    all_windows = sorted(windows, cmp=lambda x,y: x.get_x() - y.get_x())
    windows = copy(all_windows)
    active = windows[active_window_idx(windows)]
    windows = filter(lambda x: active.pos[1] + active.size[1] >= x.pos[1], windows)
    windows = filter(lambda x: active.pos[1] <= x.pos[1] + x.size[1], windows)
    windows = filter(lambda x: active == x or active.center_x() != x.center_x(), windows)
    if windows:
        idx = next(1, windows)
        if idx != None:
            windows[idx].activate()
elif sys.argv[1]=="up":
    just_this_desktop()
    windows = sorted(windows, cmp=lambda x,y: x.get_y() - y.get_y())
    all_windows = copy(windows)
    active = windows[active_window_idx(windows)]
    windows = filter(lambda x: active.pos[0] + active.size[0] >= x.pos[0], windows)
    windows = filter(lambda x: active.pos[0] <= x.pos[0] + x.size[0], windows)
    windows = filter(lambda x: active == x or active.center_y() != x.center_y(), windows)
    if windows:
        idx = next(-1, windows)
        if idx != None:
            windows[idx].activate()
elif sys.argv[1]=="down":
    just_this_desktop()
    windows = sorted(windows, cmp=lambda x,y: x.get_y() - y.get_y())
    all_windows = copy(windows)
    active = windows[active_window_idx(windows)]
    windows = filter(lambda x: active.pos[0] + active.size[0] >= x.pos[0], windows)
    windows = filter(lambda x: active.pos[0] <= x.pos[0] + x.size[0], windows)
    windows = filter(lambda x: active == x or active.center_y() != x.center_y(), windows)
    if windows:
        idx = next(1, windows)
        if idx != None:
            windows[idx].activate()
elif sys.argv[1]=="close":
    subprocess.call(['wmctrl', '-c', ':ACTIVE:'])
elif sys.argv[1]=="maximize":
    subprocess.call([
        'wmctrl', '-r', ':ACTIVE:', '-b', 'toggle,maximized_vert,maximized_horz'
    ])
elif sys.argv[1]=="vsplit":
    p = active_window.pos
    s = active_window.size
    subprocess.call([
        'wmctrl', '-r', ':ACTIVE:', '-e', '0,%s,%s,%s,%s' % (
            p[0]-OFFSET[0],p[1]-OFFSET[1],
            s[0],s[1]/2
        )
    ])
    time.sleep(1.0)
    subprocess.Popen([sys.argv[2]])
    update()
    time.sleep(1.0)
    subprocess.call([
        'wmctrl', '-r', ':ACTIVE:', '-e', '0,%s,%s,%s,%s' % (
            p[0]-OFFSET[0],
            p[1]-OFFSET[1]+s[1]/2,
            s[0],s[1]/2
        )
    ])
elif sys.argv[1]=="hsplit":
    p = active_window.pos
    s = active_window.size
    subprocess.call([
        'wmctrl', '-r', ':ACTIVE:', '-e', '0,%s,%s,%s,%s' % (
            p[0]-OFFSET[0],
            p[1]-OFFSET[1],
            s[0]/2,s[1]
        )
    ])
    time.sleep(DELAY)
    subprocess.Popen([sys.argv[2]])
    update()
    time.sleep(DELAY)
    subprocess.call([
        'wmctrl', '-r', ':ACTIVE:', '-e', '0,%s,%s,%s,%s' % (
            p[0]-OFFSET[0]+s[0]/2,
            p[1]-OFFSET[1],
            s[0]/2,s[1]
        )
    ])
elif sys.argv[1]=="fill":
    just_this_desktop()
    np = []
    ns = []
    p = 0
    s = 0
    for w in windows:
        p = copy(active_window.pos)
        s = copy(active_window.size)
        if p[0] >= w.pos[0] + w.size[0]:
            np += [(w.pos[0] + w.size[0],p[1])]
    for snap in SNAP_X:
        if p[0] >= snap:
            np += [(snap,0)]
    if np:
        np = sorted(np, cmp=lambda a,b: b[0] - a[0])[0]
    else:
        np = copy(active_window.pos)

    active_window.pos = (np[0],active_window.pos[1])
    
    for w in windows:
        p = copy(active_window.pos);
        s = copy(active_window.size)
        if p[0] + s[0] <= w.pos[0]:
            ns += [(w.pos[0]-p[0],s[1])]
    for snap in SNAP_Y:
        if p[0] + s[0] <= snap:
            ns += [(snap-p[1],0)]
    if ns:
        ns = sorted(ns, cmp=lambda a,b: a[0] - b[0])[0]
    else:
        ns = copy(active_window.size)
    
    active_window.size = (ns[0],active_window.size[1])

    np = []
    for w in windows:
        p = copy(active_window.pos)
        s = copy(active_window.size)
        if p[1] >= w.pos[1] + w.size[1]:
            np += [(p[0], w.pos[1] + w.size[1])]
    for snap in SNAP_Y:
        if p[1] >= snap:
            np += [(0,snap)]
    if np:
        np = sorted(np, cmp=lambda a,b: b[1] - a[1])[0]
    else:
        np = active_window.pos
    
    active_window.pos = (active_window.pos[0],np[1])

    ns = []
    for w in windows:
        p = copy(active_window.pos)
        s = copy(active_window.size)
        if p[1] + s[1] <= w.pos[1]:
            ns += [(s[0], w.pos[1]-p[1])]
    for snap in SNAP_Y:
        if p[1] + s[1] <= snap:
            ns += [(0,snap-p[1])]
    if ns:
        ns = sorted(ns, cmp=lambda a,b: a[1] - b[1])[0]
    else:
        ns = active_window.size
    
    active_window.size = (active_window.size[0],ns[1])
    
    x = active_window.pos[0]
    y = active_window.pos[1]
    
    diffx = max(0,x-OFFSET[0]) - (x-OFFSET[0])
    diffy = max(0,y-OFFSET[1]) - (y-OFFSET[1])

    subprocess.call([
        'wmctrl', '-r', ':ACTIVE:', '-e', '0,%s,%s,%s,%s' % (
            max(0,x-OFFSET[0]),
            max(0,y-OFFSET[1]),
            active_window.size[0] - diffx,
            active_window.size[1] - diffy
        )
    ])
elif sys.argv[1]=="snap":
    snap(active_window)
elif sys.argv[1]=="calibrate":
    # TODO: get size before and after
    subprocess.call([
        'wmctrl', '-r', ':ACTIVE:', '-e', '0,%s,%s,%s,%s' % (
            active_window.pos[0],
            active_window.pos[1],
            active_window.size[0],
            active_window.size[1]
        )
    ])
    update()
    # ...
elif sys.argv[1]=="desktop":
    subprocess.call(['wmctrl', '-s', sys.argv[2]])
elif sys.argv[1]=="switchdisplay":
    x = active_window.pos[0] + SCREEN_W,
    if x >= NUM_DISPLAYS * SCREEN_W:
        x = active_window.pos[0] % SCREEN_W
    y = active_window.pos[1]
    subprocess.call([
        'wmctrl', '-r', ':ACTIVE:', '-e', '0,%s,%s,%s,%s' % (
            max(0,int(x)-OFFSET[0]),
            max(0,int(y)-OFFSET[1]),
            active_window.size[0],
            active_window.size[1]
        )
    ])
elif sys.argv[1]=="move":
    snap(active_window)
    if sys.argv[2]=="up":
        subprocess.call(['wmctrl', '-r', ':ACTIVE:', '-e', '0,%s,%s,%s,%s' % (
            max(0,int(active_window.pos[0])-OFFSET[0]),
            max(0,int(active_window.pos[1]-GRID[1])-OFFSET[1]),
            active_window.size[0],
            active_window.size[1]
        )])
    elif sys.argv[2]=="down":
        subprocess.call(['wmctrl', '-r', ':ACTIVE:', '-e', '0,%s,%s,%s,%s' % (
            max(0,int(active_window.pos[0])-OFFSET[0]),
            max(0,int(active_window.pos[1]+GRID[1])-OFFSET[1]),
            active_window.size[0],
            active_window.size[1]
        )])
    elif sys.argv[2]=="left":
        subprocess.call(['wmctrl', '-r', ':ACTIVE:', '-e', '0,%s,%s,%s,%s' % (
            max(0,int(active_window.pos[0]-GRID[0])-OFFSET[0]),
            max(0,int(active_window.pos[1])-OFFSET[1]),
            active_window.size[0],
            active_window.size[1]
        )])
    elif sys.argv[2]=="right":
        subprocess.call(['wmctrl', '-r', ':ACTIVE:', '-e', '0,%s,%s,%s,%s' % (
            max(0,int(active_window.pos[0]+GRID[0])-OFFSET[0]),
            max(0,int(active_window.pos[1])-OFFSET[1]),
            active_window.size[0],
            active_window.size[1]
        )])
elif sys.argv[1]=="grow":
    # snap(active_window)
    sz = list(active_window.size)
    if sz[0] > sz[1]:
        sz[1] *= 2
    else:
        sz[0] *= 2
    subprocess.call(['wmctrl', '-r', ':ACTIVE:', '-e', '0,%s,%s,%s,%s' % (
        max(0,int(active_window.pos[0])-OFFSET[0]),
        max(0,int(active_window.pos[1])-OFFSET[1]),
        sz[0],
        sz[1]
    )])
    
elif sys.argv[1] == "shrink":
    # snap(active_window)
    sz = list(active_window.size)
    if sz[0] > sz[1]:
        sz[0] /= 2
    else:
        sz[1] /= 2
    subprocess.call(['wmctrl', '-r', ':ACTIVE:', '-e', '0,%s,%s,%s,%s' % (
        max(0,int(active_window.pos[0])-OFFSET[0]),
        max(0,int(active_window.pos[1])-OFFSET[1]),
        sz[0],
        sz[1]
    )])

