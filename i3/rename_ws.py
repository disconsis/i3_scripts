# TODO: renaming doesn't work the first time around if no recognized apps
# TODO: renaming doesn't work if no ":"

import i3ipc
import subprocess as proc
import fasteners
import argparse


LOCK_FILE = '/tmp/ws_name_lock'


def escape(name):
    name = '\\"'.join(name.split('"'))
    return name


@fasteners.interprocess_locked(LOCK_FILE)
def get_new_name(i3, input_name):
    input_name = escape(input_name)
    workspace = i3.get_tree().find_focused().workspace()
    count = workspace.name.count(':')
    if count in {0, 1}:
        # unnamed workspace
        apps = workspace.name.split(':')[1]
    else:
        # named workspace
        apps = workspace.name.split(':')[-1]

    new_name = "{}: {}:{}".format(workspace.num, input_name, apps)
    print(new_name)
    return new_name, workspace


def rename(i3, args):
    new_name, workspace = get_new_name(i3, ' '.join(args.name))
    if new_name != workspace.name:
        print('rename workspace to "{}"'.format(new_name))
        workspace.command('rename workspace to "{}"'.format(new_name))


@fasteners.interprocess_locked(LOCK_FILE)
def remove(i3, args):
    workspace = i3.get_tree().find_focused().workspace()
    assert workspace.name.count(':') >= 2, "invalid workspace name structure"
    split_name = workspace.name.split(':')
    new_name = ':'.join((split_name[0], split_name[-1]))
    workspace.command('rename workspace to "{}"'.format(new_name))


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    rename_parser = subparsers.add_parser('rename')
    rename_parser.add_argument('name', nargs='+')
    rename_parser.set_defaults(func=rename)
    remove_parser = subparsers.add_parser('remove')
    remove_parser.set_defaults(func=remove)
    args = parser.parse_args()
    with open('/tmp/blah', 'a') as fp:
        fp.write(str(args) + '\n')
    i3 = i3ipc.Connection()
    args.func(i3, args)


def testmain(string):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    rename_parser = subparsers.add_parser('rename')
    rename_parser.add_argument('name', nargs='+')
    rename_parser.set_defaults(func=rename)
    remove_parser = subparsers.add_parser('remove')
    remove_parser.set_defaults(func=remove)
    args = parser.parse_args(string.split())
    i3 = i3ipc.Connection()
    args.func(i3, args)


if __name__ == '__main__':
    main()
