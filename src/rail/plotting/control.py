"""Functions to control plot making in the context of a RailProject"""

from __future__ import annotations

from typing import Any

import yaml
from matplotlib.figure import Figure

from .dataset_factory import RailDatasetFactory
from .plotter_factory import RailPlotterFactory
from .plotter import RailPlotter

# Lift the RailDatasetFactory class methods

load_dataset_yaml = RailDatasetFactory.load_yaml

print_dataset_contents = RailDatasetFactory.print_contents

get_datasets = RailDatasetFactory.get_datasets

get_dataset_names = RailDatasetFactory.get_dataset_names

get_dataset_dicts = RailDatasetFactory.get_dataset_dicts

get_dataset_dict_names = RailDatasetFactory.get_dataset_dict_names

get_dataset = RailDatasetFactory.get_dataset

get_dataset_dict = RailDatasetFactory.get_dataset_dict


# Lift the RailPlotterFactory class methods

load_plotter_yaml = RailPlotterFactory.load_yaml

print_plotter_contents = RailPlotterFactory.print_contents

get_plotter_dict = RailPlotterFactory.get_plotter_dict

get_plotter_names = RailPlotterFactory.get_plotter_names

get_plotter_list_dict = RailPlotterFactory.get_plotter_list_dict

get_plotter_list_names = RailPlotterFactory.get_plotter_list_names

get_plotter = RailPlotterFactory.get_plotter

get_plotter_list = RailPlotterFactory.get_plotter_list


# Lift methods from RailPlotter

write_plots = RailPlotter.write_plots


# Define a few additional functions

def print_contents() -> None:
    """Print the contents of the factories """
    RailPlotterFactory.print_contents()
    RailDatasetFactory.print_contents()


def make_plots(
    plotter_list_name: str,
    datatset_dict_name: str,
) -> dict[str, Figure]:
    """ Make a set of plots

    Parameters
    ----------
    plotter_list_name: str
        Name of the plotter list to use to make the plots.
        This needs to have been previous loaded.

    datatset_dict_name: str
        Name of the dataset list to use to make the plots.
        This needs to have been previous loaded.

    Returns
    -------
    out_dict: dict[str, Figure]
        Dictionary of the newly created figures
    """
    plotter_list = get_plotter_list(plotter_list_name)
    dataset_dict = get_dataset_dict(datatset_dict_name)
    out_dict = RailPlotter.iterate(plotter_list, dataset_dict)
    return out_dict



class RailPlotGroup:
    """ Defining of a group on plots to make
    with a particular dataset
    """

    def __init__(
        self,
        plotter_list_name: str,
        dataset_dict_name: str,
        outdir: str=".",
        figtype: str="png",
    ):
        self.plotter_list_name = plotter_list_name
        self.dataset_dict_name = dataset_dict_name
        self.outdir = outdir
        self.figtype = figtype
        self._plots: dict[str, Figure] = {}

    def __call__(self, save: bool=True, purge: bool=True) -> dict[str, Figure]:
        """ Make all the plots given the data

        Parameters
        ----------
        save: bool
            If true, save the plots to disk

        purge: bool
            If true, delete the plots after saving

        Returns
        -------
        out_dict: dict[str, Figure]
            Dictionary of the newly created figures
        """

        self._plots.update(
            make_plots(
                self.plotter_list_name,
                self.dataset_dict_name,
            ),
        )
        if save:
            write_plots(self._plots, self.outdir, self.figtype)
            if purge:
                self._plots.clear()
        return self._plots

    @classmethod
    def create(
        cls,
        config_dict: dict[str, Any],
    ) -> RailPlotGroup:
        """ Create a RailPlotGroup object

        Parameters
        ----------
        config_dict: dict[str, Any]
            Config parameters for this group, passed to c'tor

        Returns
        -------
        plot_group: RailPlotGroup
            Newly created object
        """
        return cls(**config_dict)

    @classmethod
    def load_yaml(
        cls,
        yaml_file: str,
    ) -> dict[str, RailPlotGroup]:
        """Read a yaml file and load build the RailPlotGroup objects

        Parameters
        ----------
        yaml_file: str
            File to read

        Notes
        -----
        The yaml file should look something like this:

        PlotterYaml: <path_to_yaml_file_defining_plotter_lists>
        DatasetYaml: <path_to_yaml_file defining_dataset_lists>
        PlotsGroups:
            - PlotGroup:
                  name: some_name
                  plotter_list_name: nice_plots
                  dataset_dict_name: nice_data
            - PlotGroup:
                  name: some_other_name
                  plotter_list_name: janky_plots
                  dataset_dict_name: janky_data
        """
        out_dict: dict[str, RailPlotGroup] = {}
        with open(yaml_file, encoding="utf-8") as fin:
            all_data = yaml.safe_load(fin)

        try:
            plotter_yaml = all_data['PlotterYaml']
        except KeyError as msg:
            raise KeyError(
                "yaml file does not contain PlotterYaml key "
                f"{list(all_data.keys())}"
            ) from msg
        load_plotter_yaml(plotter_yaml)

        try:
            dataset_yaml = all_data['DatasetYaml']
        except KeyError as msg:
            raise KeyError(
                "yaml file does not contain DatasetYaml key "
                f"{list(all_data.keys())}"
            ) from msg

        try:
            group_data = all_data['PlotGroups']
        except KeyError as msg:
            raise KeyError(
                "yaml file does not contain PlotGroups key "
                f"{list(all_data.keys())}"
            ) from msg
        load_dataset_yaml(dataset_yaml)

        for group_item in group_data:
            try:
                plot_group_config = group_item["PlotGroup"]
            except KeyError as msg:
                raise KeyError(
                    "expected PlotGroup yaml block. "
                    f"{list(group_item.keys())}"
                ) from msg
            try:
                name = plot_group_config.pop("name")
            except KeyError as msg:
                raise KeyError(
                    "PlotGroup yaml block does not contain name for plot group: "
                    f"{list(plot_group_config.keys())}"
                ) from msg
            out_dict[name] = cls.create(plot_group_config)

        return out_dict


def run(
    yaml_file: str,
    include_groups: list[str] | None=None,
    exclude_groups: list[str] | None=None,
    save_plots: bool=True,
    purge_plots: bool=True,
) -> dict[str, Figure]:
    """Read a yaml file an make the corresponding plots

    Parameters
    ----------
    yaml_file: str
        Top level yaml file with definitinos

    include_groups: list[str]
        PlotGroups to explicitly include
        Use `None` for all plots

    exclude_groups: list[str]
        PlotGroups to explicity exclude
        Use `None` to not exclude anything

    save_plots: bool=True
        Save plots to disk

    purge_plots: bool=True
        Remove plots from memory after saving

    Returns
    -------
    out_dict: dict[str, Figure]
        Newly created plots.   If purge=True this will be empty
    """
    out_dict: dict[str, Figure] = {}
    group_dict = RailPlotGroup.load_yaml(yaml_file)
    if include_groups is None or not include_groups:
        include_groups = list(group_dict.keys())
    if exclude_groups is None or not exclude_groups:
        exclude_groups = []
    for exclude_group_ in exclude_groups:
        include_groups.remove(exclude_group_)

    for group_ in include_groups:
        plot_group = group_dict[group_]
        out_dict.update(plot_group(save_plots, purge_plots))
    return out_dict
