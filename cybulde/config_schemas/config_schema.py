

from hydra.core.config_store import ConfigStore
from omegaconf import MISSING
from cybulde.config_schemas import gcp_schema
from pydantic.dataclasses import dataclass


@dataclass
class Config:
    infrastructure: gcp_schema.GCPConfig = MISSING
    raw_data_gcs_location: str = "gs://cybulde/data/raw-data-from-dvc"


def setup_config():
    cs = ConfigStore.instance()
    cs.store(name="config_schema", node=Config)

    gcp_schema.setup_config()

