import logging
import logging.config
from typing import Any, Optional
from omegaconf import DictConfig, OmegaConf
import yaml

import hydra
from hydra.types import TaskFunction

from cybulde.config_schemas import raw_data_schema


def get_config(config_path: str, config_name: str):
    setup_config()
    setup_logger()

    def main_decorator(task_function: TaskFunction) -> TaskFunction:
        @hydra.main(config_path=config_path, config_name=config_name, version_base=None)
        def decorated_main(dict_config: Optional[DictConfig] = None) -> Any:
            config = OmegaConf.to_object(dict_config)
            return task_function(config)

        return decorated_main

    return main_decorator



def setup_config() -> None:
    raw_data_schema.setup_config()


def setup_logger() -> None:
    with open("./cybulde/configs/hydra/job_logging/custom.yaml", "r") as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)
