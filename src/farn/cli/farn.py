#!/usr/bin/env python
# coding utf-8

import argparse
import logging
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Tuple, Union

# Remove current directory from Python search path.
# Only through this trick it is possible that the current CLI file 'farn.py'
# carries the same name as the package 'farn' we import from in the next lines.
# If we did NOT remove the current directory from the Python search path,
# Python would start searching for the imported names within the current file (farn.py)
# instead of the package 'farn' (and the import statements fail).
# sys.path = sys.path[1:]
sys.path = [path for path in sys.path if Path(path) != Path(__file__).parent]
from farn import run_farn  # noqa E402
from farn.utils.logging import configure_logging  # noqa E402

logger = logging.getLogger(__name__)


def _argparser() -> argparse.ArgumentParser:
    parser = ArgumentParser(
        prog="farn",
        usage="%(prog)s farnDict [options [args]]",
        epilog="_________________farn___________________",
        prefix_chars="-",
        add_help=True,
        description=(
            "Run the sampling for all layers as configured in farnDict,"
            "generate the corresponding case folder structure and"
            "execute user-defined shell command sets in all case folders."
        ),
    )

    _ = parser.add_argument(
        "farnDict",
        metavar="farnDict",
        type=str,
        help="name of the dict file containing the farn configuration.",
    )

    _ = parser.add_argument(
        "-s",
        "--sample",
        action="store_true",
        help="read farn dict file, run the sampling defined for each layer and save the sampled farnDict file with prefix sampled.",
        default=False,
        required=False,
    )

    _ = parser.add_argument(
        "-g",
        "--generate",
        action="store_true",
        help="generate the folder structure that spawns all layers and cases defined in farnDict",
        default=False,
        required=False,
    )

    _ = parser.add_argument(
        "-e",
        "--execute",
        metavar="command",
        action="store",
        type=str,
        help=(
            "execute the given command set in all case folders.\n"
            "The command set must be defined in the commands section of the applicable layer in farnDict."
        ),
        default=None,
        required=False,
    )

    _ = parser.add_argument(
        "-b",
        "--batch",
        action="store_true",
        help="Executes the given command set in batch mode, i.e. asynchronously",
        default=False,
        required=False,
    )

    _ = parser.add_argument(
        "--test",
        action="store_true",
        help="Run only first case and exit. (note: --test is most useful in combination with --execute)",
        default=False,
        required=False,
    )

    console_verbosity = parser.add_mutually_exclusive_group(required=False)

    _ = console_verbosity.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="console output will be quiet.",
        default=False,
    )

    _ = console_verbosity.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="console output will be verbose.",
        default=False,
    )

    _ = parser.add_argument(
        "--log",
        action="store",
        type=str,
        help="name of log file. If specified, this will activate logging to file.",
        default=None,
        required=False,
    )

    _ = parser.add_argument(
        "--log-level",
        action="store",
        type=str,
        help="log level applied to logging to file.",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="WARNING",
        required=False,
    )

    return parser


def main():
    """Entry point for console script as configured in setup.cfg.

    Runs the command line interface and parses arguments and options entered on the console.
    """

    parser = _argparser()
    try:
        args = parser.parse_args()
    except Exception:
        parser.print_help()
        exit(0)

    # Configure Logging
    # ..to console
    log_level_console: str = (
        "INFO"  # default would usually be 'WARNING', but for farn it makes sense to set default level to 'INFO'
    )
    if any([args.quiet, args.verbose]):
        log_level_console = "ERROR" if args.quiet else log_level_console
        log_level_console = "DEBUG" if args.verbose else log_level_console
        # ..to file
    log_file: Union[Path, None] = Path(args.log) if args.log else None
    log_level_file: str = args.log_level
    configure_logging(log_level_console, log_file, log_level_file)

    farn_dict_file: Path = Path(args.farnDict)
    sample: bool = args.sample
    generate: bool = args.generate
    command: Union[str, None] = args.execute
    batch: bool = args.batch
    test: bool = args.test

    # catch missing arguments {sample, generate, command}
    # and drop an error
    # as one of them IS required
    if not sample and not generate and command is None:
        parser.print_help()
        logger.error("farn: none of the required options given: '--sample' or '--generate' or '--execute'")

    # Check whether farn dict file exists
    if not farn_dict_file.is_file():
        logger.error(f"farn: File {farn_dict_file} not found.")
        # easter egg: Generate Barnsley fern
        # _generate_barnsley_fern()
        return

    logger.info(
        f"Start farn.py with following arguments:\n"
        f"\t farn_dict_file: \t{farn_dict_file}\n"
        f"\t sample: \t\t{sample}\n"
        f"\t generate: \t\t{generate}\n"
        f"\t command: \t\t{command}\n"
        f"\t batch: \t\t\t{batch}\n"
        f"\t test: \t\t\t{test}"
    )

    # Invoke API
    _ = run_farn(
        farn_dict_file=farn_dict_file,
        sample=sample,
        generate=generate,
        command=command,
        batch=batch,
        test=test,
    )


def _generate_barnsley_fern():
    """
    easter egg: Barnsley fern.

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

    """
    import tempfile
    import tkinter as tk

    from numpy import random
    from PIL import Image
    from PIL.ImageDraw import ImageDraw

    def t1(p: Tuple[float, float]) -> Tuple[float, float]:
        """1%."""
        return (0.0, 0.16 * p[1])

    def t2(p: Tuple[float, float]) -> Tuple[float, float]:
        """85%."""
        return (0.85 * p[0] + 0.04 * p[1], -0.04 * p[0] + 0.85 * p[1] + 1.6)

    def t3(p: Tuple[float, float]) -> Tuple[float, float]:
        """7%."""
        return (0.2 * p[0] - 0.26 * p[1], 0.23 * p[0] + 0.22 * p[1] + 1.6)

    def t4(p: Tuple[float, float]) -> Tuple[float, float]:
        """7%."""
        return (-0.15 * p[0] + 0.28 * p[1], 0.26 * p[0] + 0.24 * p[1] + 0.44)

    x_size = 1024
    y_size = 1024
    im = Image.new("RGBA", (x_size, x_size))
    draw = ImageDraw(im)

    p: Tuple[float, float] = (0, 0)
    end = 20000
    ii = 0
    scale = 100
    x_offset = 512

    rng = random.default_rng()
    rnd = rng.random()
    rnd2 = rng.normal(1, 0)
    e = 1
    s = 0
    rnd3 = (rng.normal(e, s), rng.normal(e, s), rng.normal(e, s))
    while ii < end:
        rnd = rng.random()
        rnd2 = rng.normal(1, 0)
        if ii % 1 == 0:
            rnd3 = (rng.normal(e, s), rng.normal(e, s), rng.normal(e, s))
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
            fill=(int(rgb[0] * rnd3[0]), int(rgb[1] * rnd3[1]), int(rgb[2] * rnd3[2])),
        )

        ii += 1

    del draw

    with tempfile.TemporaryDirectory() as temp_dir:
        # im.save(Path(os.getenv('HOME')) / 'splash.png')
        temp_file = Path(temp_dir) / "splash.png"
        im.save(temp_file)

        root = tk.Tk()
        root.overrideredirect(True)
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(
            "%dx%d+%d+%d"
            % (
                x_size,
                y_size,
                screen_width / 2 - x_size / 2,
                screen_height / 2 - y_size / 2,
            )
        )
        # image = tk.PhotoImage(file=Path(os.getenv('HOME')) / 'splash.png')
        image = tk.PhotoImage(file=temp_file)
        canvas = tk.Canvas(root, height=y_size, width=x_size, bg="dark slate gray")
        _ = canvas.create_image(x_size / 2, y_size / 2, image=image)  # type: ignore
        canvas.pack()
        _ = root.after(3000, root.destroy)
        root.mainloop()

    return


if __name__ == "__main__":
    main()
