from hydra.core.config_store import ConfigStore
from pydantic.dataclasses import dataclass

from omegaconf import MISSING

from cybulde.config_schemas import gcp_schema
from cybulde.config_schemas.config_schema import Config


@dataclass
class RawDataConfig(Config):
    dvc_remote_name: str = "gcs-storage"
    dvc_remote_url: str = "gs://cybulde/data/raw"
    dvc_raw_data_folder: str = "data/raw"

    # For getting versioned data
    version: str = MISSING
    dvc_raw_data_remote_repo: str = "https://github.com/emkademy-handson/cybulde-data-handson.git"

    github_user_name: str = "emkademy-handson"
    github_access_token_secret_id: str = "emkademy-handson-github-access-token"

    raw_data_local_save_dir: str = MISSING



def setup_config() -> None:
    cs = ConfigStore.instance()
    cs.store(name="raw_data_schema", node=RawDataConfig)
