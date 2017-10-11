# TODO: renaming doesn't work the first time around if no recognized apps
# TODO: renaming doesn't work if no ":"

import i3ipc
import subprocess as proc
import fasteners
import argparse


LOCK_FILE = '/tmp/ws_name_lock'


@fasteners.interprocess_locked(LOCK_FILE)
def get_new_name(i3, input_name):
    workspace = i3.get_tree().find_focused().workspace()
    count = workspace.name.count(':')
    # unnamed workspace
    if count in {0, 1}:
        apps = workspace.name.split(':')[1]
    # named workspace
    elif count == 2:
        apps = workspace.name.split(':')[2]
    else:
        raise ValueError

    new_name = "{}: {}:{}".format(workspace.num, input_name, apps)
    return new_name, workspace


def rename(i3, args):
    try:
        new_name, workspace = get_new_name(i3, args.name)
    except ValueError:
        proc.call(['i3-nagbar', '-m',
                   '"too many `:` in workspace {}"'.format(workspace.num)])
        return

    if new_name != workspace.name:
        workspace.command('rename workspace "{}" to "{}"'.format(workspace.name,
                                                                 new_name))


@fasteners.interprocess_locked(LOCK_FILE)
def remove(i3, args):
    workspace = i3.get_tree().find_focused().workspace()
    assert workspace.name.count(':') == 2, "invalid workspace name structure"
    split_name = workspace.name.split(':')
    new_name = ':'.join((split_name[0], split_name[2]))
    workspace.command('rename workspace "{}" to "{}"'.format(workspace.name,
                                                             new_name))


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    rename_parser = subparsers.add_parser('rename')
    rename_parser.add_argument('name')
    rename_parser.set_defaults(func=rename)
    remove_parser = subparsers.add_parser('remove')
    remove_parser.set_defaults(func=remove)
    args = parser.parse_args()
    i3 = i3ipc.Connection()
    args.func(i3, args)


if __name__ == '__main__':
    main()
