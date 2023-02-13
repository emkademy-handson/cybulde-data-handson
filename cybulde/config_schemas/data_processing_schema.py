from hydra.core.config_store import ConfigStore
from pydantic.dataclasses import dataclass

from omegaconf import MISSING
from cybulde.config_schemas.config_schema import Config
from cybulde.config_schemas.data_processing import dataset_reader_schema, dataset_cleaner_schema
from cybulde.config_schemas.dask_cluster import dask_cluster_schema


@dataclass
class DataProcessingConfig(Config):
    dataset_reader_manager: dataset_reader_schema.DatasetReaderManagerConfig = MISSING
    dataset_cleaner_manager: dataset_cleaner_schema.DatasetCleanerManagerConfig = MISSING

    dask_cluster: dask_cluster_schema.DaskClusterConfig = MISSING
    processed_data_save_dir: str = MISSING


def setup_config() -> None:
    cs = ConfigStore.instance()

    cs.store(name="data_processing_schema", node=DataProcessingConfig)

    dataset_reader_schema.setup_config()
    dataset_cleaner_schema.setup_config()

    dask_cluster_schema.setup_config()
