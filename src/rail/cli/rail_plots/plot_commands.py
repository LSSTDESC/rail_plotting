from typing import Any

import click

from rail.core import __version__

from rail.plotting import control
from . import plot_options


@click.group()
@click.version_option(__version__)
def plot_cli() -> None:
    """RAIL plotting functions"""


@plot_cli.command(name="run")
@plot_options.save_plots()
@plot_options.purge_plots()
def run_command(**kwargs: Any) -> int:
    """Make a bunch of plots"""
    control.run(**kwargs)
    return 0
