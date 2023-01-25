from pathlib import Path

from omegaconf import OmegaConf
from cybulde.config_schemas.data_processing_schema import DataProcessingConfig
from hydra.utils import instantiate

from cybulde.utils.config_utils import get_config, remove_attribute_return_as_dict
from cybulde.utils.utils import get_logger


@get_config(config_path="../configs", config_name="data_processing_config")
def process_data(config: DataProcessingConfig) -> None:
    logger = get_logger(Path(__file__).name)
    logger.info("Processing raw data...")

    dataset_reader_manager_kwargs = remove_attribute_return_as_dict(config.dataset_reader_manager, "_dataset_readers_dict")
    dataset_reader_manager = instantiate(dataset_reader_manager_kwargs)

    df = dataset_reader_manager.read_data()

    print(df.compute().head(10))


if __name__ == "__main__":
    process_data()
