from hydra.core.config_store import ConfigStore
from pydantic.dataclasses import dataclass


@dataclass
class GCPConfig:
    project_id: str = "emkademy"


def setup_config() -> None:
    cs = ConfigStore.instance()
    cs.store(group="infrastructure", name="gcp_schema", node=GCPConfig)
