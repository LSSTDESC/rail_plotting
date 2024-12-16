from __future__ import annotations

import os
from typing import Any

import numpy as np
import tables_io
import qp

from rail.utils.project import RailProject


def extract_z_true(
    filepath: str,
    colname: str='redshift',
) -> np.ndarray:

    truth_table = tables_io.read(filepath)
    return truth_table[colname]


def extract_z_point(
    filepath: str,
    colname: str='zmode',
) -> np.ndarray:
    qp_ens = qp.read(filepath)
    z_estimates = np.squeeze(qp_ens.ancil[colname])
    return z_estimates


def extract_multiple_z_point(
    filepaths: dict[str, str],
    colname: str='zmode',
) -> dict[str, np.ndarray]:
    ret_dict = {key: extract_z_point(val, colname) for key, val in filepaths.items()}
    return ret_dict


def make_z_true_z_point_single_dicts(
    z_true: np.ndarray,
    z_estimates: dict[str, np.ndarray],
) -> dict[str, dict[str, np.ndarray]]:
    out_dict: dict[str, dict[str, np.ndarray]] = {}
    for key, val in z_estimates.items():
        out_dict[key] = dict(
            truth=z_true,
            pointEstimate=val,
        )
    return out_dict


def make_z_true_z_point_list_dict(
    z_true: np.ndarray,
    z_estimates: dict[str, np.ndarray],
) -> dict[str, Any]:
    out_dict: dict[str, Any] = dict(
        truth=z_true,
        pointEstimates=z_estimates,
    )
    return out_dict


def get_z_true_path(
    project: RailProject,
    selection: str,
    flavor: str,
    tag: str,
) -> str:
    return project.get_file_for_flavor(flavor, tag, selection=selection)


def get_ceci_pz_output_paths(
    project: RailProject,
    selection: str,
    flavor: str,
    algos: list[str] = ['all'],
) -> dict[str, str]:

    if 'all' in algos:
        algos = list(project.get_pzalgorithms().keys())

    out_dict = {}
    outdir = project.get_path('ceci_output_dir', selection=selection, flavor=flavor)
    for algo_ in algos:
        basename = f"output_estimate_{algo_}.hdf5"
        outpath = os.path.join(outdir, basename)
        if os.path.exists(outpath):
            out_dict[algo_] = outpath
    return out_dict
