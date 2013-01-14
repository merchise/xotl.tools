#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#----------------------------------------------------------------------
# xoutil.fs.dupfind
#----------------------------------------------------------------------
# Copyright (c) 2012 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License (GPL) as published by the
# Free Software Foundation;  either version 2  of  the  License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Created on 2012/12/26

'''
Works similar to Paul Sundvall's 'rdfind' but programmed in Python.

Finds duplicate files in directories, and takes appropriate actions.

Use an storage system based on 'HashingIndexex'. 'DictHashingIndexer' is
provided with a basic implementation based in a Python 'dict'.

A rank is assigned to each file in order to figure out which file is the
best candidate for being the original meaning that if a file is found on
several places, the one found with the higher rank is the proposed to be
kept (the others are considered duplicates).

It can be used as a Python module or as an command line application.

Usage when used as an application:

    dupfind [options] dir-1 dir-2 ...


Options are:

    --make-symlinks
            Replace duplicate files with symbolic links.

    --make-hardlinks
            Replace duplicate files with hard links.

    -d, --delete
            Delete duplicate files.

    --backup=DIR
            With this option, duplicated files are moved to a backup directory.
            You control where the backup file goes through the parameter DIR.
            If it is not specified the standard temporal directory is used.

    --safe
            Execute dangerous duplicate file processing -like delete- after
            detection process has completed, not during.

    --list-only
            Replace the standard output with duplicate files name in order to
            concatenate this command with the execution of 'xargs' in a pipe.
            No internal action is executed, so this option is incompatible
            with delete and backup actions.

    --results=FILE
            Create a file with a report similar to command 'rdfind', if the
            parameter FILE is not specified 'result.txt' is generated.

    --filter=PATTERN
            Exclude files matching simple shell-style wild-cards a la
            'fnmatch'.
            In filters, the character '/' will be converted to the character
            used by the operating system to separate pathname components. This
            is the proper '/' for POSIX and '\\' for Windows.
            Filtered files are all treated always as not duplicated.

            Patterns are Unix shell style:
                *         matches everything
                ?         matches any single character
                [seq]     matches any character in seq
                [!seq]    matches any char not in seq

    --filter-regex=PATTERN
            Exclude files matching a regular expression. Remember that to
            include a '\' character you must double it (\\).
            Filtered files are all treated always as not duplicated.

    --filter-size=SIZE
            Exclude files which size is less than that SIZE. If this option is
            not specified SIZE is assumed as "1". Use "0" to include all files.
            Filtered files are all treated always as not duplicated.

    --find=FILE
            Search for a file in specified workspace using content comparing.

            Create the hash index for locating matching files inside the
            workspace defined for all folders specified as arguments.

            This option implies "--list-only", if you want to change this
            behavior increment verbose level (-v) or use "--results".

    -c, --checksum
            This changes the way 'dupfind' checks if the files are duplicated
            or not. By default 'dupfind' uses a "quick method" that checks
            each file’s size, then first and last four bytes of each content.
            If the "quick method" is not good enough, without this option,
            'dupfind' will compare at most 128 bytes from the middle of each
            file content, and with this option compare a 256-bit MD5 checksum
            for each file that has matching size and first and last four bytes.

    --sleep=X
            Sleep for X milliseconds between each file reads processing.

    -l, --follow-symlinks
            Follow symbolic links. Those which point inside any specified tree,
            always are ignored.

    --out-format=FORMAT
            Output each file processing using the specified FORMAT
            Note that the names of the processed files that are output are
            done using a default of "{name}{link}", which tells you just the
            name of the file and, if the item is a link, where it points in
            the format '-> original-path'.

            Format specifiers could be:
                {name}    full file name
                {link}    where a symbolic link points to, or blank string if
                          the item is not a symbolic link.

    -v, --verbose
            This option increases the amount of information you are given
            during the file processing. By default, 'dupfind' works almost
            silently (statistic information).
            A single '-v' will give you information about what files are being
            processed and a brief summary at the end.
            Two '-v' options will give you also information on what files are
            being skipped and slightly more information at the end.
            More than two '-v' options should only be used if you are
            debugging 'dupfind'.

    --version
            Show program's version and exit

    -h, --help
            Show the help for the command.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _absolute_import)

__docstring_format__ = 'rst'
__author__ = 'med'
__version__ = 0.9


# ============ Main Application Section ============

MSG_START = 'Scanning "%s".'
MSG_FILES_FOUND = '%s files in total.'
MSG_DISCARDED_DEVICE = 'Discarded %s files due to non-unique device and inode.'
MSG_SIZE_START = 'Discarding files with %s size from list...'
MSG_REMOVED_LEFT = 'removed %s files from list. %s files left.'
MSG_TOTAL_SIZE = 'Total size is %s bytes or %s.'
MSG_DISCARDED_SIZE = ('Discarded %s files due to unique sizes from list.'
                      ' %s files left.')
MSG_FIRST_BYTES = 'Eliminating candidates based on first bytes:'
MSG_LAST_BYTES = 'Eliminating candidates based on last bytes:'
MSG_MIDDLE_BYTES = 'Eliminating candidates based on middle bytes:'
MSG_CHECKSUM = 'Eliminating candidates based on md5 checksum:'
MSG_NOT_UNIQUE = 'It seems like you have %s files that are not unique.'
MSG_SIZE_REDUCED = 'Totally, %s can be reduced.'
MSG_MAKING_FILE = 'Now making results file "%s".'



# Delete or link actions
ACTION_NONE = 0
ACTION_DELETE = 1
ACTION_CREATE_SYMLINKS = 2
ACTION_CREATE_HARDLINKS = 3
ACTION_BACKUP = 4


def get_options():
    from argparse import ArgumentParser, Action
    from xoutil.config.argparse import store_also

    class TestAction(Action):
        def __init__(self, *args, **kwargs):
            super(TestAction, self).__init__(*args, **kwargs)
            print('='*20, '__init__:', args, kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            print('='*20, '__call__:', '\n\tparser:', parser,
                  '\n\tnamespace:', namespace, '\n\tvalues:', values,
                  '\n\toption_string:', option_string)
            setattr(namespace, self.dest, values)

    parser = ArgumentParser(description='See "xoutil.fs.dupfind" help for more'
                            ' information.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--delete', dest='action',
        action='store_const', const=ACTION_DELETE, default=ACTION_NONE,
        help='delete duplicate files')
    group.add_argument('--make-symlinks', dest='action', action='store_const',
        const=ACTION_CREATE_SYMLINKS,
        help='replace duplicate files with symbolic links')
    group.add_argument('--make-hardlinks', dest='action', action='store_const',
        const=ACTION_CREATE_HARDLINKS,
        help='replace duplicate files with hard links')
    group.add_argument('--backup', metavar='BACKUP_DIR', nargs='?', const='',
        action=store_also(action=ACTION_BACKUP),
        help='duplicated files are moved to a backup directory')
    parser.add_argument('--safe', action='store_true', default=False,
        help='execute dangerous duplicate file processing after detection '
                'process has completed.')
    parser.add_argument('--list-only', action='store_true', default=False,
        help='replace standard output just with duplicate files')
    parser.add_argument('--results', metavar='FILE', nargs='?',
        help='create a file with a report similar to "rdfind"')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--filter', metavar='PATTERN',
        help='exclude files matching simple shell-style wild-cards a la '
             '"fnmatch"')
    group.add_argument('--filter-regex', metavar='PATTERN',
        help='exclude files matching a regular expression')
    parser.add_argument('--filter-size', metavar='SIZE', type=int, default=1,
        help='exclude files which size is less than that SIZE')
    parser.add_argument('--find', metavar='FILE',
        help='search for a file in specified workspace using content '
             'comparing.')
    parser.add_argument('-c', '--checksum', action='store_true', default=False,
        help='use "md5" hash for hard duplicate file compare')
    parser.add_argument('--sleep', metavar='MILISECONDS', type=int, default=0,
        help='sleep for a time between each file processing')
    parser.add_argument('-l', '--follow-symlinks',
        action='store_true', default=False,
        help='follow symbolic links')
    parser.add_argument('--out-format',
        metavar='FORMAT',
        help='output each file processing using the specified FORMAT')
    parser.add_argument('-v', '--verbose', action='count',
        help='amount of information you are given during the file processing')
    parser.add_argument('--version', action='version', version=__version__,
        help="show program's version and exit")
    parser.add_argument('workspace', nargs='*', metavar='FOLDER',
        help='workspace is defined using 0 or more folder paths; if none, CWD '
             'is assumed.')

    args = parser.parse_args()
    return args


args = get_options()

if __name__ == '__main__':
    print(args, type(args))
    
