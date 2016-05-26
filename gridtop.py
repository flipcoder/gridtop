#!/usr/bin/env python2

import sys
import subprocess
from copy import copy

class Window:
    def __init__(self, name, line,):
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
    
windows = []
lines = subprocess.check_output(['wmctrl', '-G', '-l']).split('\n')
lines = lines[:-1]
for i in range(len(lines)):
    lines[i] = lines[i].split(' ')
    lines[i] = filter(lambda x: x, lines[i])
    name = ' '.join(lines[i][6:])
    lines[i] = lines[i][:6]
    windows += [Window(name, lines[i])]
    if windows[i].num == active_window_num:
        windows[i].active = True

if sys.argv[1]=="left":
    all_windows = sorted(windows, cmp=lambda x,y: x.get_x() - y.get_x())
    windows = copy(all_windows)
    windows = sorted(windows, cmp=lambda x,y: x.get_x() - y.get_x())
    active = windows[active_window_idx(windows)]
    windows = filter(lambda x: active.pos[1] + active.size[1] >= x.pos[1], windows)
    windows = filter(lambda x: active.pos[1] <= x.pos[1] + x.size[1], windows)
    windows = filter(lambda x: active == x or active.center_x() != x.center_x(), windows)
    print windows
    if windows:
        idx = next(-1, windows)
        if idx != None:
            windows[idx].activate()
elif sys.argv[1]=="right":
    all_windows = sorted(windows, cmp=lambda x,y: x.get_x() - y.get_x())
    windows = copy(all_windows)
    active = windows[active_window_idx(windows)]
    windows = filter(lambda x: active.pos[1] + active.size[1] >= x.pos[1], windows)
    windows = filter(lambda x: active.pos[1] <= x.pos[1] + x.size[1], windows)
    windows = filter(lambda x: active == x or active.center_x() != x.center_x(), windows)
    idx = next(1, windows)
    windows[idx].activate()
elif sys.argv[1]=="up":
    windows = sorted(windows, cmp=lambda x,y: x.get_y() - y.get_y())
    all_windows = copy(windows)
    active = windows[active_window_idx(windows)]
    windows = filter(lambda x: active.pos[0] + active.size[0] >= x.pos[0], windows)
    windows = filter(lambda x: active.pos[0] <= x.pos[0] + x.size[0], windows)
    windows = filter(lambda x: active == x or active.center_y() != x.center_y(), windows)
    idx = next(-1, windows)
    windows[idx].activate()
elif sys.argv[1]=="down":
    windows = sorted(windows, cmp=lambda x,y: x.get_y() - y.get_y())
    all_windows = copy(windows)
    active = windows[active_window_idx(windows)]
    windows = filter(lambda x: active.pos[0] + active.size[0] >= x.pos[0], windows)
    windows = filter(lambda x: active.pos[0] <= x.pos[0] + x.size[0], windows)
    windows = filter(lambda x: active == x or active.center_y() != x.center_y(), windows)
    idx = next(-1, windows)
    windows[idx].activate()

