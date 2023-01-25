from hydra.core.config_store import ConfigStore
from pydantic.dataclasses import dataclass

from omegaconf import MISSING
from cybulde.config_schemas.config_schema import Config
from cybulde.config_schemas.data_processing import dataset_reader_schema


@dataclass
class DataProcessingConfig(Config):
    dataset_reader_manager: dataset_reader_schema.DatasetReaderManagerConfig = MISSING


def setup_config() -> None:
    cs = ConfigStore.instance()

    cs.store(name="data_processing_schema", node=DataProcessingConfig)

    dataset_reader_schema.setup_config()
