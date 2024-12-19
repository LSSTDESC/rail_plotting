from typing import Any

import click

from rail.core import __version__

from rail.cli.rail_pipe import pipe_options
from rail.plotting import control
from . import plot_options


@click.group()
@click.version_option(__version__)
def plot_cli() -> None:
    """RAIL plotting functions"""


@plot_cli.command(name="run")
@pipe_options.config_file()
@plot_options.include_groups()
@plot_options.exclude_groups()
@plot_options.save_plots()
@plot_options.purge_plots()
def run_command(config_file: str, **kwargs: Any) -> int:
    """Make a bunch of plots"""
    print(kwargs)
    #control.run(config_path, **kwargs)
    return 0
