from __future__ import annotations

import os

from ceci.config import StageConfig, StageParameter


class RailPlotter:
    """ Base class for making matplotlib plot """
    
    config_options: dict[str, StageParameter] = {}
    
    _inputs: dict = {}

    plotter_classes = {}

    def __init_subclass__(cls):
        cls.plotter_classes[cls.__name__] = cls

    @classmethod
    def print_classes(cls):
        for key, val in cls.plotter_classes.items():
            print(f"{key} {val}")

    @classmethod
    def get_plotter_class(cls, name):
        try:
            return cls.plotter_classes[name]
        except KeyError as msg:
            raise KeyError(f"Could not find plotter class {name} in {list(cls.plotter_classes.keys())}") from msg

    @staticmethod
    def load_plotter_class(class_name):        
        tokens = class_name.split('.')
        module = '.'.join(tokens[:-1])
        class_name = tokens[-1]
        __import__(module)
        plotter_class = RailPlotter.get_plotter_class(class_name)
        return plotter_class
        
    @staticmethod
    def create_from_dict(
        name: str, 
        config_dict: dict[str, Any],
    ) -> RailPlotter:
        copy_config = config_dict.copy()
        class_name = copy_config.pop('class_name')
        plotter_class = RailPlotter.load_plotter_class(class_name)
        return plotter_class(name, **copy_config)

    @staticmethod
    def iterate_plotters(
        plotters: list[RailPlotter],
        prefix: str,
        **kwargs: Any,
    ) -> dict[str, matplotlib.Figure]:
        """ Utility function to several plotters on the same data 

        Parameters
        ----------
        plotters: list[RailPlotter]
            Plotters to run

        prefix: str
            Prefix to append to plot names, e.g., the p(z) algorithm or
            analysis 'flavor'

        kwargs: dict[str, Any]
            Used to pass the data to make the plots

        Returns
        -------
        out_dict: dict[str, matplotlib.Figure]
            Dictionary of the newly created figures
        """
        out_dict: dict[str, matplotlib.Figure] = {}
        for plotter_ in plotters:
            out_dict.update(plotter_(prefix, **kwargs))
        return out_dict

    @staticmethod
    def iterate(
        plotters: list[RailPlotter],
        data_dict: dict[str, dict],
    ) -> dict[str, matplotlib.Figure]:
        """ Utility function to several plotters of several data sets

        Parameters
        ----------
        plotters: list[RailPlotter]
            Plotters to run

        data_dict: dict[str, dict]
            Prefixes and datasets to iterate over

        Returns
        -------
        out_dict: dict[str, matplotlib.Figure]
            Dictionary of the newly created figures
        """
        out_dict: dict[str, matplotlib.Figure] = {}
        for key, val in data_dict.items():
            out_dict.update(RailPlotter.iterate_plotters(plotters, key, **val))
        return out_dict
            
    @staticmethod
    def save_plots(
        fig_dict: dict[str, matplotlib.Figure],
        outdir: str=".", 
        figtype: str="png",
    ) -> None:
        """ Utility function to several plotters of several data sets

        Parameters
        ----------
        fig_dict: dict[str, matplotlib.Figure]
            Dictionary of figures to save

        outdir: str
            Directory to save figures in

        figtype: str
            Type of figures to save, e.g., png, pdf...
        """
        for key, val in fig_dict.items():
            try:
                os.makedirs(outdir)
            except:
                pass
            out_path = os.path.join(outdir, f"{key}.{figtype}")
            val.savefig(out_path)        
            
    def __init__(self, name: str, **kwargs: Any):
        """ C'tor
        
        Parameters
        ----------
        name: str
            Name for this plotter, used to construct names of plots
        
        kwargs: Any
            Configuration parameters for this plotter, must match
            class.config_options data members
        """        
        self._name = name
        self._config = StageConfig(**self.config_options)
        self._set_config(**kwargs)

    @property
    def config(self) -> StageConfig:
        return self._config
        
    def __repr__(self) -> str:
        return f"{self._name}"

    def __call__(self, prefix: str, **kwargs: Any) -> dict[str, matplotlib.Figure]:
        """ Make all the plots given the data

        Parameters
        ----------
        prefix: str
            Prefix to append to plot names, e.g., the p(z) algorithm or
            analysis 'flavor'

        kwargs: dict[str, Any]
            Used to pass the data to make the plots

        Returns
        -------
        out_dict: dict[str, matplotlib.Figure]
            Dictionary of the newly created figures
        """
        self._validate_inputs(**kwargs)
        return self._make_plots(prefix, **kwargs)

    def _make_full_plot_name(self, prefix: str, plot_name: str) -> str:
        """ Create the make for a specific plot

        Parameters
        ----------
        prefix: str
            Prefix to append to plot names, e.g., the p(z) algorithm or
            analysis 'flavor'

        plot_name: str
            Specific name for a particular plot
        
        Returns
        -------
        plot_name: str
            Plot name, following the pattern f"{self._name}_{prefix}_{plot_name}"
        """
        return f"{self._name}_{prefix}_{plot_name}"
    
    def _set_config(self, **kwargs: Any) -> None:
        kwcopy = kwargs.copy()
        for key in self.config.keys():
            if key in kwargs:
                self.config[key] = kwcopy.pop(key)
            else:
                attr = self.config.get(key)
                if attr.required:
                    raise ValueError(f"Missing configuration option {key}")
                self.config[key] = attr.default
        if kwcopy:
            raise ValueError(f"Unrecogonized configruation parameters {kwcopy.keys()}")
    
    @classmethod
    def _validate_inputs(cls, **kwargs: Any) -> None:
        for key, expected_type in cls._inputs.items():
            try:
                data = kwargs[key]
            except KeyError as msg:
                raise KeyError(
                    f"{key} not provided to RailPlotter {self._name} in {list(kwargs.keys())}"
                ) from msg
            if not isinstance(data, expected_type):
                raise TypeError(f"{key} provided to RailPlotter was {type(data)}, expected {expected_type}")

    def _make_plots(self, prefix: str, **kwargs: Any) -> dict[str, matplotlib.Figure]:
        raise NotImplementedError()


    