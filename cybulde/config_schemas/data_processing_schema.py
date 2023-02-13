from hydra.core.config_store import ConfigStore
from pydantic.dataclasses import dataclass

from omegaconf import MISSING
from cybulde.config_schemas.config_schema import Config
from cybulde.config_schemas.data_processing import dataset_reader_schema, dataset_cleaner_schema


@dataclass
class DataProcessingConfig(Config):
    dataset_reader_manager: dataset_reader_schema.DatasetReaderManagerConfig = MISSING
    dataset_cleaner_manager: dataset_cleaner_schema.DatasetCleanerManagerConfig = MISSING


def setup_config() -> None:
    cs = ConfigStore.instance()

    cs.store(name="data_processing_schema", node=DataProcessingConfig)

    dataset_reader_schema.setup_config()
    dataset_cleaner_schema.setup_config()
