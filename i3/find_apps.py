#!/usr/bin/python3

import subprocess as proc
import i3ipc
from collections import defaultdict
import re
import fasteners
import yaml
import os
import sys

SETTINGS_FILE = 'settings.yaml'


def classify_windows(i3):
    "get list of windows in each workspace"

    windows = i3.get_tree().leaves()
    with fasteners.InterProcessLock(settings['files']['LAST_LOCK_FILE']):
        try:
            with open(settings['files']['LAST_FOCUSED_FILE']) as fp:
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
    colors = settings['colors']
    apps = []
    for window in windows:
        if window.name is None:
            continue
        app = get_app(window)
        if window == focused_window:
            app = "<span foreground='{0}'>{1}</span>".format(
                colors['focused'],
                app if app is not None else settings['glyphs']['unknown']
            )
        elif window == last_focused_win:
            app = "<span foreground='{0}'>{1}</span>".format(
                colors['last focused'],
                app if app is not None else settings['glyphs']['unknown']
            )
        if app is not None:
            apps.append(app)
    return apps


def get_app(window):
    try:
        glyphs = settings['glyphs']
        # download manager
        if window.window_class == 'Uget-gtk':
            match = re.fullmatch('^uGet(?: - (?P<num>\d+) tasks)?$', window.name)
            num_tasks = match.group('num')
            if num_tasks is not None:
                return glyphs['download manager'] + ' +' + num_tasks
            else:
                return glyphs['download manager']
        # browser/youtube
        elif window.window_class in ('Firefox', 'Google-chrome', 'qutebrowser'):
            match = re.fullmatch(
                r'^(?:(?P<url>.+) - )?(?P<browser>Mozilla Firefox|Vimperator|Google Chrome|qutebrowser)(?P<private> \(Private Browsing\))?$',
                window.name
            )
            if match is None:
                return glyphs['browser']
            url = match.group('url')
            if url is not None and url.endswith('- YouTube'):
                return glyphs['youtube']
            else:
                return glyphs['browser']
        # tor browser
        elif window.window_class == 'Tor Browser':
            return glyphs['tor']
        # ebook reader
        elif window.window_class in ('Okular', 'Zathura'):
            return glyphs['ebook reader']
        # virtual machine
        elif window.window_class in ('Vmplayer', 'VirtualBox'):
            return glyphs['virtual machine']
        # media player
        elif window.window_class and window.window_class.lower() == 'vlc':
            return glyphs['media player']
        # wireshark
        elif window.window_class == "Wireshark":
            return glyphs['wireshark']
        # terminal
        if window.window_class in ('Gnome-terminal', 'URxvt', 'XTerm',
                                   'st-256color'):
            return glyphs['terminal']
        # file browser
        elif window.window_class == "Nautilus":
            return glyphs['file browser']
        # image viewer/editor
        elif window.window_class in ('Pinta', 'Pqiv', 'feh', 'Eog'):
            return glyphs['image viewer']
        # fontforge
        elif window.window_class == 'fontforge':
            return glyphs['fontforge']
        # office
        elif window.window_class and window.window_class.startswith('libreoffice'):
            return glyphs['office']
        # gvim
        elif window.window_class == 'Gvim':
            return glyphs['gvim']
        # editor
        elif window.window_class == 'Gedit':
            return glyphs['editor']
        # spim
        elif window.window_class == 'QtSpim':
            if window.name == 'Console':
                return None
            return glyphs['spim']
        # android studio
        elif window.window_class == 'jetbrains-studio' \
                and window.window_instance == 'sun-awt-X11-XFramePeer' \
                and 'Android Studio' in window.name.split(' - ')[-1]:
            return glyphs['android studio']
        # burp suite
        elif window.name.startswith('Burp Suite'):
            return glyphs['burp suite']
        else:
            return None

    except Exception as err:
        print(err, file=sys.stdout)
        print(window.__dict__, file=sys.stdout)
        if not settings['debug'] is True:  # continue if not debugging, else break
            return None
        else:
            raise err


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
            workspace.name, new_name
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
            with fasteners.InterProcessLock(settings['files']['LOCK_FILE']):
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
    i3 = i3ipc.Connection()
    if len(sys.argv) > 1:
        if len(sys.argv) == 2 and sys.argv[1] == 'debug':
            for window in i3.get_tree().leaves():
                print(
                    "name: {:80}\nclass: {}\ninstance: {}\nrole: {}".format(
                        window.name, window.window_class,
                        window.window_instance, window.window_role
                ))
                print('---')
        else:
            print("usage:")
            print("\t{} -> start daemon".format(sys.argv[0]))
            print("\t{} debug -> list current windows".format(sys.argv[0]))
        exit(0)

    try:
        with open(os.path.join(sys.path[0], SETTINGS_FILE)) as fp:
            settings = yaml.load(fp)
    except Exception as err:
        print("[!] Couldn't load settings")
        print(("[!] Ensure that '{}' is in the same directory as"
               " this script").format(SETTINGS_FILE))
        print("="*20)
        print(err)
        exit(1)

    rename_everything(i3, None)
    i3.on('workspace::focus', rename_everything)
    i3.on('window::focus', rename_everything)
    i3.on('window::move', rename_everything)
    i3.on('window::title', rename_everything)
    i3.on('window::close', rename_everything)
    i3.main()
