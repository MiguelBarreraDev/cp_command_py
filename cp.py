#!/usr/bin/python3
"""
This module implements objects for a program that simulates in parte
the behavior of the CLI 'cp'
"""
import argparse
from pathlib import Path
from sys import stderr, stdout


class CpError(Exception):
    pass


class Logger:
    def __init__(self, verbosity=False):
        self.verbose = verbosity

    def set_verbosity(self, verbosity):
        self.verbose = verbosity

    def log(self, message, file=stdout):
        if self.verbose:
            print(message)

    def warn(self, message, file=stderr):
        print(f'Warning: {message}', file=file)

    def error(self, message, file=stderr):
        print(f'Error: {message}', file=stderr)

logger = Logger()

def dump(src: Path, dest: Path):
    with open(src, 'rb') as sf, open(dest, 'wb') as df:
        df.write(sf.read())


def copy_directory(src_dir: Path, dest_dir: Path, force=False, interactive=False):
    for src_child in src_dir.iterdir():
        dest_child = dest_dir / src_child.name
        if src_child.is_dir():
            logger.log(f'Copy dir {src_child} -> {dest_child}')
            dest_child.mkdir(exist_ok=True)
            copy_directory(src_child, dest_child, force, interactive)
        elif src_child.is_file():
            confirmed = True
            if dest_child.is_file():
                if interactive:
                    confirmed = 'y' in input(f'Force {dest_child} ? [NO/Yes]').lower()
                elif not force:
                    confirmed = False
            if confirmed:
                logger.log(f'Copy file {src_child} -> {dest_child}')
                dest_child.touch()
                dump(src_child, dest_child)
            else:
                logger.log(f'Skipping {src_child} -> {dest_child}')
        else:
            logger.error(f'Skipping {src_child} because file type is not supported')


def copy_file(src: Path, dest: Path, force=False):
    if dest.is_dir():
        dest = dest / src.name
    if dest.is_file() and not force:
        raise CpError(f'Cannot override {dest}, specify -f option')
    logger.log(f"copy src:{src} -> dest:{dest}")
    dest.touch()
    dump(src, dest)


def copy(src: Path, dest: Path, force=False, recursive=False, interactive=False):
    """
    Function definition
    """
    if src.is_file():
        copy_file(src, dest, force)
    elif src.is_dir():
        dest_is_dir = dest.is_dir()
        if not dest_is_dir and dest.exists():
            raise CpError(f'Destination {dest} is not a directory')
        if not recursive:
            raise CpError(f'Skipping directory {src} because -r option is not present')
        if dest_is_dir:
            dest = dest / src.name
        dest.mkdir(exist_ok=True)
        copy_directory(src, dest, force, interactive)
    else:
        raise CpError('File type not supported')


def cli() -> argparse.Namespace:
    """
    functions definition wich is responsible for defining the input
    structure entered by command line
    """
    parser = argparse.ArgumentParser(
        prog='cp',
        description="""
        cp command implemented in python language, whose functions
        is to copy files and directories from a source to a destination
        """
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Given details about actions being performed'
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Override destination files if they alredy exist'
    )
    group.add_argument(
        '-f', '--force',
        action='store_true',
        help='Override destination files if they alredy exist'
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Copy directories recursively'
    )
    parser.add_argument(
        'source',
        type=Path,
        help="Source directory or file"
    )
    parser.add_argument(
        'destination',
        type=Path,
        help="Destination directory or file"
    )

    return parser.parse_args()


def main():
    """
    Define the main actions of the program
    """
    args = cli()
    try:
        logger.set_verbosity(args.verbose)
        copy(args.source, args.destination, args.force, args.recursive, args.interactive)
    except CpError as err:
        logger.error(err)
        exit(1)
    except KeyboardInterrupt:
      print('\nInterrupted', file=stderr)

if __name__ == '__main__':
    main()
