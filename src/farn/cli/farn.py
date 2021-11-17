#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__      = "DNV"
__copyright__   = "Copyright THIS_YEAR, github.com/dnv-opensource"
__credits__     = ["Claas Rostock", "Seunghyeon Yoo", "Frank Lumpitzsch"]
__description__ = """generate and manipulate deeply nested case structures, apply arbitrary sampling and hierarchical or non-hierarchical filtering"""
__email__       = "n.n.@dnv.com"
__license__     = "MIT"
__maintainer__  = "n.n."
__prog__        = "farn"
__status__      = "Development"
__version__     = "MAJOR_VERSION.MINOR_VERSION.PATCH_VERSION"


import logging
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Union

# Remove current directory from Pathon search path.
# Only through this trick it is possible that the current CLI file 'farn.py'
# carries the same name as the package 'farn' we import from in the next lines.
# If we did NOT remove the current directory from the Python search path,
# Python would start searching for the imported names within the current file (farn.py)
# instead of the package 'farn' (and the import statements fail).
# sys.path = sys.path[1:]
sys.path = [path for path in sys.path if Path(path) != Path(__file__).parent]
from farn.farn import run_farn                      # noqa E402
from farn.utils.logging import configure_logging    # noqa E402


logger = logging.getLogger(__name__)


def cli():

    parser = ArgumentParser(
        prog=__prog__,
        usage=f'{__prog__} [options [args]] FARNDICT',
        epilog='_'*17+__prog__+'_'*17,
        prefix_chars='-',
        add_help=True,
        description=(__description__)
    )

    parser.add_argument(
        'farnDict',
        metavar='FARNDICT',
        type=str,
        help='name of the dict file containing the farn configuration.',
    )

    parser.add_argument(
        '-s',
        '--sample',
        action='store_true',
        help=
        'read farn dict file, run the sampling defined for each layer and save the sampled farn dict file with prefix sampled.',
        default=False,
        required=False,
    )

    parser.add_argument(
        '-g',
        '--generate',
        action='store_true',
        help='generate the folder structure that spawns all layers and cases defined in farnDict',
        default=False,
        required=False,
    )

    parser.add_argument(
        '-e',
        '--execute',
        metavar='COMMAND',
        action='store',
        type=str,
        help=(
            'execute the given command in all case folders.\n'
            'The command must be defined in the commands section of the applicable layer in farnDict.'
        ),
        default=None,
        required=False,
    )

    parser.add_argument(
        '--ignore-errors',
        action='store_true',
        help='do not halt on errors',
        default=False,
        required=False,
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='run only first case and then exit',
        default=False,
        required=False,
    )

    console_verbosity = parser.add_mutually_exclusive_group(required=False)

    console_verbosity.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help='console output will be quiet.',
        default=False,
    )

    console_verbosity.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='console output will be verbose.',
        default=False,
    )

    parser.add_argument(
        '--log',
        action='store',
        type=str,
        help='name of log file. If specified, this will activate logging to file.',
        default=None,
        required=False,
    )

    parser.add_argument(
        '--log-level',
        action='store',
        type=str,
        help='log level applied to logging to file.',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='WARNING',
        required=False,
    )

    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        exit(0)

    # Configure Logging
    # ..to console
    log_level_console: str = 'INFO'
    if any([args.quiet, args.verbose]):
        log_level_console = 'ERROR' if args.quiet else log_level_console
        log_level_console = 'DEBUG' if args.verbose else log_level_console
    # ..to file
    log_file: Union[Path, None] = Path(args.log) if args.log else None
    log_level_file: str = args.log_level
    configure_logging(log_level_console, log_file, log_level_file)

    farn_dict_file: Path = Path(args.farnDict)
    run_sampling: bool = args.sample
    generate: bool = args.generate
    command: str = args.execute
    ignore_errors: bool = args.ignore_errors
    test: bool = args.test

    # catch missing arguments {sample, generate, command}
    # and drop an error
    # as one of them IS required
    if (run_sampling==False and generate==False and command==None):
        parser.print_help()
        logger.error(f"farn: none of the required options given: '--sample' or '--generate' or '--execute'")

    main(
        farn_dict_file=farn_dict_file,
        run_sampling=run_sampling,
        generate=generate,
        command=command,
        ignore_errors=ignore_errors,
        test=test,
    )


def main(
    farn_dict_file: Path,
    run_sampling: bool = False,
    generate: bool = False,
    command: str = None,
    ignore_errors: bool = False,
    test: bool = False,
):
    # Check whether farn dict file exists
    if not farn_dict_file.is_file():
        logger.error(f"farn: File {farn_dict_file} not found.")
        # easter egg: Generate Barnsley fern
        _generate_barnsley_fern()
        return

    run_farn(
        farn_dict_file=farn_dict_file,
        run_sampling=run_sampling,
        generate=generate,
        command=command,
        ignore_errors=ignore_errors,
        test=test,
    )

    return


def _generate_barnsley_fern():
    '''
    easter egg: Barnsley fern

    Barnsley Fern:
            ┌     ┐ ┌   ┐   ┌   ┐
            | a b | | x |   | e |
    ƒ(x,y) = |     | |   | + |   |
            | c d | | y |   | f |
            └     ┘ └   ┘   └   ┘
    w	a	b	c	d	e	f	p	Portion generated
    ƒ1	0	0	0	0.16	0	0	0.01	Stem
    ƒ2	0.85	0.04	−0.04	0.85	0	1.60	0.85	Successively smaller leaflets
    ƒ3	0.20	−0.26	0.23	0.22	0	1.60	0.07	Largest left-hand leaflet
    ƒ4	−0.15	0.28	0.26	0.24	0	0.44	0.07	Largest right-hand leaflet

    '''
    import os
    import tkinter as tk

    from numpy import random
    from PIL import Image
    from PIL.ImageDraw import ImageDraw

    def t1(p):
        '''
        1%
        '''
        return (0, 0.16 * p[1])

    def t2(p):
        '''
        85%
        '''
        return (0.85 * p[0] + 0.04 * p[1], -0.04 * p[0] + 0.85 * p[1] + 1.6)

    def t3(p):
        '''
        7%
        '''
        return (0.2 * p[0] - 0.26 * p[1], 0.23 * p[0] + 0.22 * p[1] + 1.6)

    def t4(p):
        '''
        7%
        '''
        return (-0.15 * p[0] + 0.28 * p[1], 0.26 * p[0] + 0.24 * p[1] + 0.44)

    x_size = 1024
    y_size = 1024
    im = Image.new('RGBA', (x_size, x_size))
    draw = ImageDraw(im)

    p = (0, 0)
    end = 20000
    ii = 0
    scale = 100
    x_offset = 512

    rng = random.default_rng()
    rnd = rng.random()
    rnd2 = rng.normal(1, 0)
    E = 1
    S = 0
    rnd3 = (rng.normal(E, S), rng.normal(E, S), rng.normal(E, S))
    while ii < end:
        rnd = rng.random()
        rnd2 = rng.normal(1, 0)
        if ii % 1 == 0:
            rnd3 = (rng.normal(E, S), rng.normal(E, S), rng.normal(E, S))
        rgb = [148, 204, 48]
        if rnd <= (0.01 * rnd2):
            p = t1(p)
        elif rnd > (0.01 * rnd2) and rnd <= (0.86 * rnd2):
            p = t2(p)
        elif rnd > (0.86 * rnd2) and rnd <= (0.93 * rnd2):
            p = t3(p)
        else:
            p = t4(p)
        # ImageDraw.Draw(im,)
        draw.point(
            (p[0] * scale + x_offset, p[1] * scale),
            fill=(int(rgb[0] * rnd3[0]), int(rgb[1] * rnd3[1]), int(rgb[2] * rnd3[2]))
        )

        ii += 1

    del draw

    im.save(Path(os.getenv('HOME')) / 'splash.png')

    root = tk.Tk()
    root.overrideredirect(True)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(
        '%dx%d+%d+%d' %
        (x_size, y_size, screen_width / 2 - x_size / 2, screen_height / 2 - y_size / 2)
    )
    image = tk.PhotoImage(file=Path(os.getenv('HOME')) / 'splash.png')
    canvas = tk.Canvas(root, height=y_size, width=x_size, bg="dark slate gray")
    canvas.create_image(x_size / 2, y_size / 2, image=image)
    canvas.pack()
    root.after(3000, root.destroy)
    root.mainloop()

    return


if __name__ == '__main__':
    cli()
