#!/usr/bin/python3

# TODO: map glyphs in separate file

import subprocess as proc
import i3ipc
from collections import defaultdict
import re
import fasteners
from rename_ws import escape
import yaml
import os
import sys


GLYPH_FILE = 'glyphs.yaml'
FOCUSED_COLOR = 'cyan'
LAST_FOCUSED_COLOR = 'white'
LOCK_FILE = '/tmp/ws_name_lock'
LAST_LOCK_FILE = '/tmp/last_win_lock'
LAST_FOCUSED_FILE = '/tmp/i3_last_focused'


def classify_windows(i3):
    "get list of windows in each workspace"
    windows = i3.get_tree().leaves()
    with fasteners.InterProcessLock(LAST_LOCK_FILE):
        try:
            with open(LAST_FOCUSED_FILE) as fp:
                last_id = int(fp.read())
        except FileNotFoundError:
            last_id = None
    workspace_content = defaultdict(list)
    focused_window = None
    last_focused_window = None
    for window in windows:
        workspace_content[window.workspace()].append(window)
        if window.focused is True:
            focused_window = window
        elif window.id == last_id:
            last_focused_window = window
    return workspace_content, focused_window, last_focused_window


def find_apps(windows, focused_window=None, last_focused_win=None):
    apps = []
    for window in windows:
        if window.name is None:
            continue
        app = get_app(window)
        if window == focused_window:
            app = "<span foreground='{0}'>{1}</span>".format(
                FOCUSED_COLOR,
                app if app is not None else '?'
            )
        elif window == last_focused_win:
            app = "<span foreground='{0}'>{1}</span>".format(
                LAST_FOCUSED_COLOR,
                app if app is not None else '?'
            )
        if app is not None:
            apps.append(app)
    return apps


def get_app(window):
    # download manager
    if window.window_class == 'Uget-gtk':
        match = re.fullmatch('^uGet(?: - (?P<num>\d+) tasks)?$', window.name)
        num_tasks = match.group('num')
        if num_tasks is not None:
            return glyphs['download manager'] + ' +' + num_tasks
        else:
            return glyphs['download manager']
    # browser/youtube
    elif window.window_class in ('Firefox', 'Google-chrome'):
        match = re.match(
            '^(?:(?P<url>.+) - )?(?P<browser>Mozilla Firefox|Vimperator|Google Chrome)',
            window.name
        )
        if match is None:
            # probably a stupid title like "confirm"
            # in a floating window
            return None
        url = match.group('url')
        if url is not None and url.endswith('- YouTube'):
            return glyphs['youtube']
        else:
            return glyphs['browser']
    # ebook reader
    elif window.window_class == 'Okular':
        return glyphs['ebook reader']
    # virtual machine
    elif window.window_class in ('Vmplayer', 'VirtualBox'):
        return glyphs['virtual machine']
    # media player
    elif window.window_class == 'vlc':
        return glyphs['media player']
    # wireshark
    elif window.window_class == "Wireshark":
        return glyphs['wireshark']
    # terminal
    if window.name in ('Terminal', 'urxvt'):
        return glyphs['terminal']
    # file browser
    elif window.window_class == "Nautilus":
        return glyphs['file browser']
    # image viewer/editor
    elif window.window_class in ('Pinta', 'Pqiv'):
        return glyphs['image viewer']
    # fontforge
    elif window.window_class == 'fontforge':
        return glyphs['fontforge']
    else:
        return None


def get_new_name(workspace, apps):
    count = workspace.name.count(':')
    if count in {0, 1}:
        # unnamed workspace
        new_name = '{}: {}'.format(workspace.num, ' '.join(apps))
    else:
        # named workspace
        custom_name = ':'.join(workspace.name.split(':')[1:-1])
        new_name = '{}:{}: {}'.format(workspace.num, custom_name,
                                      ' '.join(apps))
    return new_name


def rename_workspace(i3, workspace, windows, focused_window=None,
                     last_focused_win=None):
    if not len(windows):
        return
    apps = find_apps(windows, focused_window, last_focused_win)
    new_name = get_new_name(workspace, apps)
    if new_name != workspace.name:
        i3.command('rename workspace "{}" to "{}"'.format(
            escape(workspace.name), escape(new_name)
        ))


def rename_everything(i3, e):
    workspace_list = i3.get_workspaces()
    workspace_content, focused_window, last_focused_win = classify_windows(i3)
    focused_workspace = (focused_window.workspace()
                         if focused_window is not None
                         else None)
    for workspace in workspace_content.keys():
        windows = workspace_content[workspace]
        if workspace == focused_workspace:
            with fasteners.InterProcessLock(LOCK_FILE):
                rename_workspace(i3, workspace, windows,
                                 focused_window, last_focused_win)
        else:
            rename_workspace(i3, workspace, windows,
                             focused_window, last_focused_win)
    filled_workspaces = [w.name for w in workspace_content.keys()]
    for workspace in workspace_list:
        if workspace.name not in filled_workspaces:
            i3.command('rename workspace "{}" to "{}"'.format(
                workspace.name,
                str(workspace.num))
            )


if __name__ == '__main__':
    with open(os.path.join(sys.path[0], GLYPH_FILE)) as fp:
        glyphs = yaml.load(fp)
    i3 = i3ipc.Connection()
    i3.on('workspace::focus', rename_everything)
    i3.on('window::focus', rename_everything)
    i3.on('window::move', rename_everything)
    i3.on('window::title', rename_everything)
    i3.on('window::close', rename_everything)
    i3.main()
