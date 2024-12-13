from __future__ import annotations

import numpy as np
from matplotlib import pyplot as plt
from ceci.config import StageParameter

from .plotter import RailPlotter


class PZPlotterPointEstimateVsTrueHist2D(RailPlotter):
    """ Class to make a 2D histogram of p(z) point estimates 
    versus true redshift
    """    
    
    config_options: dict[str, StageParameter] = dict(
        z_min=StageParameter(float, 0., fmt="%0.2f", msg="Minimum Redshift"),
        z_max=StageParameter(float, 3., fmt="%0.2f", msg="Maximum Redshift"),
        n_zbins=StageParameter(int, 150, fmt="%0.2f", msg="Number of z bins"),
    )

    inputs: dict = {
        'truth':np.array,
        'pointEstimate':np.array,
    }

    def _make_2d_hist_plot(self, **kwargs) -> matplotlib.Figure:
        figure, axes = plt.subplots()
        bin_edges = np.linspace(self.config.z_min, self.config.z_max, self.config.n_zbins+1)
        axes.hist2d(
            kwargs['truth'],
            kwargs['pointEstimate'],
            bins=(bin_edges, bin_edges),
        )
        plt.xlabel("True Redshift")
        plt.ylabel("Estimated Redshift")
        return figure


    def _make_plots(self, prefix: str, **kwargs: Any) -> dict[str, matplotlib.Figure]:
        out_dict: dict[str, matplotlib.Figure]  = {}
        out_dict[self._make_full_plot_name(prefix, 'hist')] = self._make_2d_hist_plot(**kwargs)
        return out_dict


class PZPlotterPointEstimateVsTrueProfile(RailPlotter):
    """ Class to make a profile plot of p(z) point estimates 
    versus true redshift
    """    

    config_options: dict[str, StageParameter] = dict(
        z_min=StageParameter(float, 0., fmt="%0.2f", msg="Minimum Redshift"),
        z_max=StageParameter(float, 3., fmt="%0.2f", msg="Maximum Redshift"),
        n_zbins=StageParameter(int, 150, fmt="%0.2f", msg="Number of z bins"),
    )

    inputs: dict = {
        'truth':np.array,
        'pointEstimate':np.array,
    }

    def _make_2d_profile_plot(self, **kwargs) -> matplotlib.Figure:
        figure, axes = plt.subplots()
        bin_edges = np.linspace(self.config.z_min, self.config.z_max, self.config.n_zbins+1)
        bin_centers = 0.5*(bin_edges[0:-1] + bin_edges[1:])
        z_true_bin = np.searchsorted(bin_edges, kwargs['truth'])
        z_estimates = kwargs['pointEstimate']
        means = np.zeros((self.config.n_zbins))
        stds = np.zeros((self.config.n_zbins))
        for i in range(self.config.n_zbins):
            mask = z_true_bin == i
            data = z_estimates[mask]
            if len(data) == 0:
                continue
            means[i] = np.mean(data) - bin_centers[i]
            stds[i] = np.std(data)

        axes.errorbar(
            bin_centers,
            means,
            stds,
        )
        plt.xlabel("True Redshift")
        plt.ylabel("Estimated Redshift")
        return figure

    def _make_plots(self, prefix: str, **kwargs: Any) -> dict[str, matplotlib.Figure]:
        out_dict: dict[str, matplotlib.Figure]  = {}
        out_dict[self._make_full_plot_name(prefix, 'profile')] = self._make_2d_profile_plot(**kwargs)
        return out_dict


class PZPlotterAccuraciesVsTrue(RailPlotter):
    """ Class to make a plot of the accuracy of several algorithms  
    versus true redshift
    """    

    config_options: dict[str, StageParameter] = dict(
        z_min=StageParameter(float, 0., fmt="%0.2f", msg="Minimum Redshift"),
        z_max=StageParameter(float, 3., fmt="%0.2f", msg="Maximum Redshift"),
        n_zbins=StageParameter(int, 150, fmt="%0.2f", msg="Number of z bins"),
        delta_cutoff=StageParameter(float, 0.1, fmt="%0.2f", msg="Delta-Z Cutoff for accurary"),
    )

    inputs: dict = {
        'truth':np.array,
        'pointEstimates':dict[str, np.array],
    }

    def _make_accuracy_plot(self, **kwargs) -> matplotlib.Figure:
        figure, axes = plt.subplots()
        bin_edges = np.linspace(self.config.z_min, self.config.z_max, self.config.n_zbins+1)
        bin_centers = 0.5*(bin_edges[0:-1] + bin_edges[1:])
        z_true = kwargs['truth']
        z_true_bin = np.searchsorted(bin_edges, z_true)
        z_estimates = kwargs['pointEstimates']
        for key, val in z_estimates.items():
            deltas = val - z_true
            accuracy = np.ones((self.config.n_zbins))*np.nan
            for i in range(self.config.n_zbins):
                mask = z_true_bin == i
                data = deltas[mask]
                if len(data) == 0:
                    continue
                accuracy[i] = (np.abs(data) <= self.config.delta_cutoff).sum() / float(len(data))
            axes.plot(
                bin_centers,
                accuracy,
                label=key,
            )
        plt.xlabel("True Redshift")
        plt.ylabel("Estimated Redshift")
        return figure


    def _make_plots(self, prefix: str, **kwargs: Any) -> dict[str, matplotlib.Figure]:
        out_dict: dict[str, matplotlib.Figure]  = {}
        out_dict[self._make_full_plot_name(prefix, 'accuracy')] = self._make_accuracy_plot(**kwargs)
        return out_dict
