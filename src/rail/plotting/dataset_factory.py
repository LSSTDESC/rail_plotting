from __future__ import annotations

from typing import Any

import yaml

from .data_extraction import RailProjectDataExtractor


class RailDatasetFactory:
    """Factory class to make datasets

    Expected usage is that user will define a yaml file with the various
    datasets that they wish to use with the following example syntax:

    - Dataset:
          name: gold_baseline_test
          extractor: rail.plotters.pz_data_extraction.PZPointEstimateDataExtractor
          selection: gold
          flavor: baseline
          tag: test
          algos: ['all']
    - Dataset:
          name: blend_baseline_test
          exctractor: rail.plotters.pz_data_extraction.PZPointEstimateDataExtractorxs
          selection: blend
          flavor: baseline
          tag: test
          algos: ['all']

    And group them into lists of dataset that can be run over particular types
    of data, using the following example syntax:

    - DatasetList:
          name: baseline_test
          datasets:
              - gold_baseline_test
              - blend_baseline_test
    """
    _instance: RailDatasetFactory | None = None

    def __init__(self) -> None:
        """C'tor, build an empty RailDatasetFactory"""        
        self._dataset_dict: dict[str, dict] = {}
        self._dataset_list_dict: dict[str, list[dict]] = {}

    @classmethod
    def instance(cls) -> RailDatasetFactory:
        """Return the singleton instance of the factory"""
        if cls._instance is None:
            cls._instance = RailDatasetFactory()
        return cls._instance

    @classmethod
    def print_contents(cls) -> None:
        """Print the contents of the factory """
        if cls._instance is None:
            cls._instance = RailDatasetFactory()
        cls._instance.print_instance_contents()

    @classmethod
    def load_yaml(cls, yaml_file: str) -> None:
        """Load a yaml file

        Parameters
        ----------
        yaml_file: str
            File to read and load

        Notes
        -----
        The format of the yaml file should be
 
        - Dataset:
              name: gold_baseline_test
              extractor: rail.plotters.pz_data_extraction.PZPointEstimateDataExtractor
              selection: gold
              flavor: baseline
              tag: test
              algos: ['all']
        - Dataset:
              name: blend_baseline_test
              extractor: rail.plotters.pz_data_extraction.PZPointEstimateDataExtractor
              selection: blend
              flavor: baseline
              tag: test
              algos: ['all']
        - DatasetList:
              name: baseline_test
              datasets:
                  - gold_baseline_test
                  - blend_baseline_test
        """
        if cls._instance is None:
            cls._instance = RailDatasetFactory()
        cls._instance.load_instance_yaml(yaml_file)

    @classmethod
    def get_dataset(cls, name: str) -> dict:
        """Get dataset it's assigned name

        Parameters
        ----------
        name: str
            Name of the dataset to return

        Returns
        -------
        dataset: dict
            Dataset in question
        """
        try:
            return cls.instance().dataset_dict[name]
        except KeyError as msg:
            raise KeyError(
                f"Dataset named {name} not found in RailDatasetFactory "
                f"{list(cls.instance().dataset_dict.keys())}"
            ) from msg

    @classmethod
    def get_dataset_list(cls, name: str) -> list[dict]:
        """Get a list of datasets their assigned name

        Parameters
        ----------
        name: str
            Name of the dataset list to return

        Returns
        -------
        datasets: list[dict]
            Datasets in question
        """
        try:
            return cls.instance().dataset_list_dict[name]
        except KeyError as msg:
            raise KeyError(
                f"DatasetList named {name} not found in RailDatasetFactory "
                f"{list(cls.instance().dataset_list_dict.keys())}"
            ) from msg

    @property
    def dataset_dict(self) -> dict[str, dict]:
        """Return the dictionary of individual datasets"""
        return self._dataset_dict

    @property
    def dataset_list_dict(self) -> dict[str, list[dict]]:
        """Return the dictionary of lists of datasets"""        
        return self._dataset_list_dict

    def print_instance_contents(self) -> None:
        """Print the contents of the factory"""
        print("Datasets:")
        for dataset_name, dataset in self.dataset_dict.items():
            print(f"  {dataset_name}: {dataset}")
        print("----------------")
        print("DatasetLists")
        for dataset_list_name, dataset_list in self.dataset_list_dict.items():
            print(f"  {dataset_list_name}: {dataset_list}")

    def _get_extractor(self, class_name: str) -> RailProjectDataExtractor:
        try:
            extractor_class = RailProjectDataExtractor.get_extractor_class(class_name)
        except KeyError:
            extractor_class = RailProjectDataExtractor.load_extractor_class(class_name)
        return extractor_class(class_name)

    def _make_dataset(self, name: str, class_name: str, **kwargs: Any) -> dict:
        if name in self._dataset_dict:
            raise KeyError(f"Dataset {name} is already defined")
        extractor = self._get_extractor(class_name)
        dataset = extractor(**kwargs)
        self._dataset_dict[name] = dataset
        return dataset

    def _make_dataset_list(
        self, name: str, dataset_list: list[str]
    ) -> list[dict]:
        if name in self._dataset_list_dict:
            raise KeyError(f"DatasetList {name} is already defined")
        datasets: list[dict] = []
        for dataset_name in dataset_list:
            try:
                dataset = self._dataset_dict[dataset_name]
            except KeyError as msg:
                raise KeyError(
                    f"Dataset {dataset_name} used in DatasetList "
                    f"is not found {list(self._dataset_dict.keys())}"
                ) from msg
            datasets.append(dataset)
        self._dataset_list_dict[name] = datasets
        return datasets

    def load_instance_yaml(self, yaml_file: str) -> None:
        """Read a yaml file and load the factory accordingly

        Parameters
        ----------
        yaml_file: str
            File to read

        Notes
        -----
        See `RailDatasetFactory.load_yaml` for yaml file syntax
        """
        with open(yaml_file, encoding="utf-8") as fin:
            dataset_data = yaml.safe_load(fin)

        for dataset_item in dataset_data:
            if "Dataset" in dataset_item:
                dataset_config = dataset_item["Dataset"]
                try:
                    name = dataset_config.pop("name")
                except KeyError as msg:
                    raise KeyError(
                        "Dataset yaml block does not contain name for dataset: "
                        f"{list(dataset_config.keys())}"
                    ) from msg
                try:
                    extractor = dataset_config.pop("extractor")
                except KeyError as msg:
                    raise KeyError(
                        "Dataset yaml block does not contain extractor for dataset: "
                        f"{list(dataset_config.keys())}"
                    ) from msg

                self._make_dataset(name, extractor, **dataset_config)
            elif "DatasetList" in dataset_item:
                dataset_list_config = dataset_item["DatasetList"]
                try:
                    name = dataset_list_config.pop("name")
                except KeyError as msg:
                    raise KeyError(
                        "DatasetList yaml block does not contain name for dataset: "
                        f"{list(dataset_list_config.keys())}"
                    ) from msg
                try:
                    datasets = dataset_list_config.pop("datasets")
                except KeyError as msg:
                    raise KeyError(
                        "DatasetList yaml block does not contain dataset: "
                        f"{list(dataset_list_config.keys())}"
                    ) from msg
                self._make_dataset_list(name, datasets)
            else:
                good_keys = ["Dataset", "DatasetList"]
                raise KeyError(
                    f"Expecting one of {good_keys} not: {dataset_data.keys()})"
                )
