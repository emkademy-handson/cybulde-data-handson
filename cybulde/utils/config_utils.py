from dataclasses import asdict
import logging
import logging.config

from typing import Any, Optional

import hydra
import yaml

from hydra.types import TaskFunction
from omegaconf import DictConfig, OmegaConf

from cybulde.config_schemas import config_schema, raw_data_schema, data_processing_schema


def get_config(config_path: str, config_name: str) -> TaskFunction:
    setup_config()
    setup_logger()

    def main_decorator(task_function: TaskFunction) -> Any:
        @hydra.main(config_path=config_path, config_name=config_name, version_base=None)
        def decorated_main(dict_config: Optional[DictConfig] = None) -> Any:
            config = OmegaConf.to_object(dict_config)
            return task_function(config)

        return decorated_main

    return main_decorator


def setup_config() -> None:
    config_schema.setup_config()
    data_processing_schema.setup_config()
    raw_data_schema.setup_config()


def setup_logger() -> None:
    with open("./cybulde/configs/hydra/job_logging/custom.yaml", "r") as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)


def remove_attribute_return_as_dict(config: Any, *parameters_to_remove) -> dict[str, Any]:
    config_as_dict = asdict(config)
    for parameter_to_remove in parameters_to_remove:
        del config_as_dict[parameter_to_remove]
    return config_as_dict
