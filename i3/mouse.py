#!/usr/bin/python3

import os
import pyautogui as pag
import subprocess
import sys


mouse_check = "/tmp/mouse_check"


if len(sys.argv) != 2 or sys.argv[1] not in ('toggle', 'enable', 'disable'):
    print("usage: {} {{toggle, enable, disable}}".format(sys.argv[0]))
    exit(1)


def get_id(line):
    return next(word for word in line.split() if 'id=' in word).split('=')[1]


todo = sys.argv[1]
dev_list = subprocess.check_output(['xinput', 'list']).decode('utf-8')
default_device = 'touchpad' if 'touchpad' in dev_list.lower() else 'mouse'

if todo == 'toggle':
    dev_pr_line = next(line for line in dev_list.split('\n')
                       if default_device in line.lower())
    dev_pr_id = get_id(dev_pr_line)
    dev_pr_list = subprocess.check_output(['xinput', 'list',
                                           dev_pr_id]).decode('utf-8')
    state = ('disabled' if 'This device is disabled' in dev_pr_list
             else 'enabled')
    if state == 'disabled':
        todo = 'enable'
    else:
        todo = 'disable'

dev_ptr_ids = [get_id(line) for line in dev_list.split('\n')
               if 'touchpad' in line.lower()
               or 'mouse' in line.lower()]

if todo == 'enable':
    for ptr_id in dev_ptr_ids:
        subprocess.call(['xinput', '--enable', ptr_id])
        subprocess.call(['pkill', 'unclutter'])
        subprocess.call(['touch', mouse_check])
elif todo == 'disable':
    for ptr_id in dev_ptr_ids:
        subprocess.call(['xinput', '--disable', ptr_id])
        subprocess.call(['pkill', 'unclutter'])
        os.system('unclutter -idle 0.1 &')
        try:
            os.delete(mouse_check)
        except Exception:
            pass
        pag.moveTo(pag.size())
else:
    raise
