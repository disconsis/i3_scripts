#!/usr/bin/python3

# TODO: highlight last focused window

import subprocess as proc
import i3ipc
from collections import defaultdict
import re
import fasteners
import pickle
# import posix_ipc as posix


FOCUSED_COLOR = 'cyan'
LAST_FOCUSED_COLOR = 'yellow'
LOCK_FILE = '/tmp/ws_name_lock'
LAST_LOCK_FILE = '/tmp/last_win_lock'
LAST_FOCUSED_FILE = '/tmp/i3_last_focused'
IFACES_LIST = '/tmp/ifaces.pickle'
# SEMAPHORE_NAME = '/i3_last_sema'


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
        app = get_app(window.name)
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


def get_app(title):

    # download manager
    download_regex = re.compile('^uGet( - (\d+) tasks)?$')
    match = download_regex.fullmatch(title)
    if match is None:
        pass
    elif match.groups() == (None, None):
        return ''
    else:
        num_tasks = match.group(2)
        print(match.groups())
        return ' +{}'.format(num_tasks)

    # browser
    browser_regex = [
        re.compile('^((.+) - )?Mozilla Firefox$'),
        re.compile('^((.+) - )?Vimperator$'),
    ]
    for reg in browser_regex:
        match = reg.fullmatch(title)
        if match is None:
            continue
        elif len(match.groups()) == 1:  # implies no subtitle
            return ''
        else:
            yt_regex = re.compile('^(.+ - )?YouTube$')
            if yt_regex.fullmatch(str(match.group(2))):
                return ''
            return ''

    # pdf viewer
    okular_regex = re.compile('^(.+ – )?Okular$')  # IMP: the dash is abnormal
    if okular_regex.fullmatch(title):
        return ''

    # virtual machines
    vm_regex = [
        re.compile(('^(.+ - )?VMware Workstation 12'
                    ' Player (Non-commercial use only)$')),
        re.compile('^(.+ (\[.+\]) - )?Oracle VM VirtualBox Manager$')
    ]
    for reg in vm_regex:
        if reg.fullmatch(title):
            return ''

    media_regex = re.compile('^(.* - )?VLC media player$')
    if media_regex.fullmatch(title):
        return ''

    # Wireshark
    try:
        ifaces = pickle.load(IFACES_LIST)
    except Exception as err:
        ifaces = []
        out = proc.check_output('ip link show up'.split()).decode('utf-8')
        for i, line in enumerate(out.splitlines()):
            if i % 2 == 0:
                iface = line.split()[1][:-1]
                ifaces.append('Loopback: {}'.format(iface) if iface == 'lo'
                              else iface)
        try:
            with open(IFACES_LIST, 'wb') as fp:
                pickle.dump(ifaces, fp)
        except Exception as err:
            print(2, 'Error in writing ifaces to {_list}: {err}'.format(
                _list=IFACES_LIST, err=err
            ))

    iface_re_group = '({})'.format('|'.join('{}'.format(iface)
                                            for iface in ifaces))
    wireshark_regex = [re.compile('^The Wireshark Network Analyzer$'),
                       re.compile('^Capturing from {}$'.format(iface_re_group)),
                       re.compile('^\*{}'.format(iface_re_group))]
    for regex in wireshark_regex:
        if regex.match(title):
            return ''

    # terminal
    if title in ('Terminal', 'urxvt'):
        # return ''
        return ''

    return None


def get_new_name(workspace, apps):
    # unnamed workspace
    count = workspace.name.count(':')
    if count in {0, 1}:
        new_name = '{}: {}'.format(workspace.num, ' '.join(apps))
    # named workspace
    elif count == 2:
        custom_name = workspace.name.split(':')[1]
        new_name = '{}:{}: {}'.format(workspace.num, custom_name,
                                      ' '.join(apps))
    else:
        raise ValueError
    return new_name


def rename_workspace(i3, workspace, windows, focused_window=None,
                     last_focused_win=None):
    if not len(windows):
        return
    apps = find_apps(windows, focused_window, last_focused_win)
    try:
        new_name = get_new_name(workspace, apps)
    except ValueError:
        proc.call(['i3-nagbar', '-m',
                   '"too many `:` in workspace {}"'.format(workspace.num)])
        return
    else:
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
    i3 = i3ipc.Connection()
    i3.on('workspace::focus', rename_everything)
    i3.on('window::focus', rename_everything)
    i3.on('window::move', rename_everything)
    i3.on('window::title', rename_everything)
    i3.on('window::close', rename_everything)
    i3.main()
