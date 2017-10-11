import pyautogui as pag
import os
import sys
import subprocess

DEFAULT_DEVICE = 'touchpad'  # if laptop or 'mouse' if desktop

if len(sys.argv) != 2 or sys.argv[1] not in ('toggle', 'enable', 'disable'):
    exit(1)


def get_id(line):
    return next(word for word in line.split() if 'id=' in word).split('=')[1]


todo = sys.argv[1]
dev_list = subprocess.check_output(['xinput', 'list'])

if todo == 'toggle':
    dev_pr_line = next(line for line in dev_list.split('\n')
                       if DEFAULT_DEVICE in line.lower())
    dev_pr_id = get_id(dev_pr_line)
    dev_pr_list = subprocess.check_output(['xinput', '--list', dev_pr_id])
    state = ('disabled' if 'This device is disabled' in dev_pr_list
             else 'enabled')
    if state == 'disabled':
        todo = 'enable'
    else:
        todo = 'disable'

dev_ptr_ids = [get_id(line) for line in dev_list.split('\n')
               if 'touchpad' in line.lower()
               or 'mouse' in line.lower()]

mouse_check = "/home/ketan/.config/i3blocks/flags/mouse_check"
if todo == 'enable':
    for ptr_id in dev_ptr_ids:
        subprocess.call(['xinput', '--enable', ptr_id])
        subprocess.call(['pkill', 'unclutter'])
        subprocess.call(['touch', mouse_check])
else:  # disable
    for ptr_id in dev_ptr_ids:
        subprocess.call(['xinput', '--disable', ptr_id])
        subprocess.call(['pkill', 'unclutter'])
        os.system('unclutter -idle 0.1 &')
        subprocess.call(['rm', mouse_check])
        pag.moveTo(pag.size())
