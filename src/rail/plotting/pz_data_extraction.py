from __future__ import annotations

from typing import Any

from rail.utils.project import RailProject

from .data_extraction import RailProjectDataExtractor
from .data_extraction_funcs import get_pz_point_estimate_data


class PZPointEstimateDataExtractor(RailProjectDataExtractor):
    """ Class to make a 2D histogram of p(z) point estimates
    versus true redshift
    """

    inputs: dict = {
        'project':RailProject,
        'selection':str,
        'flavor':str,
        'tag':str,
        'algos':list[str],
    }

    def _get_data(self, **kwargs: Any) -> dict[str, Any]:
        return get_pz_point_estimate_data(**kwargs)
