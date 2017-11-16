#/usr/bin/python3

import yaml
import os
import sys
import i3ipc
import subprocess as proc
import fasteners
import argparse

SETTINGS_FILE = 'settings.yaml'


def escape(name):
    "no \', \" or : allowed in the custom workspace name"

    name = ''.join(name.split('\''))
    name = ''.join(name.split('"'))
    name = ''.join(name.split(':'))
    return name


def change_num(i3, workspace, num):
    "change the workspace number"

    new_name = ":".join([str(num)] + workspace.name.split(':')[1:])
    if workspace.name != new_name:
        i3.command('rename workspace "{}" to "{}"'.format(
            workspace.name, new_name
        ))


def rename(i3, args):
    "change the workspace name/number according to the given input name"

    curr_ws = i3.get_tree().find_focused().workspace()
    input_name = escape(' '.join(args.name))

    # if no name is given, remove workspace name and finish
    if input_name == '':
        return remove(i3, args)

    if len(input_name) == 1 and input_name.isdigit() and input_name != '0':
        # input_name is a workspace number

        try:
            # workspace to swap numbers with
            swap_ws = (w for w in i3.get_workspaces()
                       if w.num == int(input_name)).__next__()

        except StopIteration:
            # no workspace to swap numbers with
            # simply change workspace number
            change_num(i3, curr_ws, int(input_name))

        else:
            # swap workspace numbers with swap_ws
            # through tmp number 0
            curr_num = curr_ws.num
            change_num(i3, swap_ws, 0)
            change_num(i3, curr_ws, int(input_name))
            swap_ws = (w for w in i3.get_workspaces()
                       if w.num == 0).__next__()
            change_num(i3, swap_ws, curr_num)

    else:
        # input_name is a custom name

        ws_name_elems = curr_ws.name.split(":")
        if len(ws_name_elems) in (1, 2):
            # <num> / <num>:<apps>
            new_name = ":".join(
                [ws_name_elems[0]] + [' ' + input_name] + ws_name_elems[1:]
            )

        elif len(ws_name_elems) == 3:
            # <num>:<name>:<apps>
            new_name = ":".join(
                [ws_name_elems[0]] + [' ' + input_name] + ws_name_elems[2:]
            )

        else:
            raise ValueError("Too many ':' in workspace name")

        if curr_ws.name != new_name:
            curr_ws.command('rename workspace to "{}"'.format(new_name))


def remove(i3, args):
    "remove workspace name"

    workspace = i3.get_tree().find_focused().workspace()
    assert workspace.name.count(':') == 2, "invalid workspace name structure"
    split_name = workspace.name.split(':')
    new_name = ':'.join((split_name[0], split_name[-1]))
    workspace.command('rename workspace to "{}"'.format(new_name))


def parse_args():
    "parse argument on the command line"

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    rename_parser = subparsers.add_parser('rename')
    rename_parser.add_argument('name', nargs='+')
    rename_parser.set_defaults(func=rename)
    remove_parser = subparsers.add_parser('remove')
    remove_parser.set_defaults(func=remove)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    i3 = i3ipc.Connection()
    with fasteners.InterProcessLock(settings['files']['LOCK_FILE']):
        args.func(i3, args)


if __name__ == '__main__':
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

    main()
