
from hydra.core.config_store import ConfigStore

from dataclasses import field
from omegaconf import MISSING
from pydantic.dataclasses import dataclass


@dataclass
class DatasetReaderConfig:
    _target_: str = MISSING
    dataset_dir: str = MISSING
    dev_set_ratio: float = 0.3
    test_set_ratio: float = 0.3
    dataset_name: str = MISSING
    

@dataclass
class GHCDatasetReaderConfig(DatasetReaderConfig):
    _target_: str = "cybulde.data_processing.dataset_readers.GHCDatasetReader"


@dataclass
class JigsawToxicCommentsDatasetReaderConfig(DatasetReaderConfig):
    _target_: str = "cybulde.data_processing.dataset_readers.JigsawToxicCommentsDatasetReader"


@dataclass
class TwitterDatasetReaderConfig(DatasetReaderConfig):
    _target_: str = "cybulde.data_processing.dataset_readers.TwitterDatasetReader"


@dataclass
class DatasetReaderManagerConfig:
    _target_: str = "cybulde.data_processing.dataset_readers.DatasetReaderManager"
    dataset_readers: list[DatasetReaderConfig] = field(default_factory=lambda: [])
    _dataset_readers_dict: dict[str, DatasetReaderConfig] = field(default_factory=lambda: {})


def setup_config() -> None:
    cs = ConfigStore.instance()

    cs.store(group="dataset_reader_manager/dataset_reader", name="ghc_dataset_reader_schema", node=GHCDatasetReaderConfig)
    cs.store(group="dataset_reader_manager/dataset_reader", name="jtc_dataset_reader_schema", node=JigsawToxicCommentsDatasetReaderConfig)
    cs.store(group="dataset_reader_manager/dataset_reader", name="twitter_dataset_reader_schema", node=TwitterDatasetReaderConfig)
    cs.store(group="dataset_reader_manager", name="dataset_reader_manager_schema", node=DatasetReaderManagerConfig)

