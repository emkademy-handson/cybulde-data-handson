from hydra.core.config_store import ConfigStore

from pydantic.dataclasses import dataclass


@dataclass
class RawDataConfig:
    dvc_remote_name: str = "gcs-storage"
    dvc_remote_url: str = "gs://cybulde/data"
    dvc_raw_data_folder: str = "data/raw"


def setup_config() -> None:
    cs = ConfigStore.instance()
    cs.store(name="raw_data_schema", node=RawDataConfig)


