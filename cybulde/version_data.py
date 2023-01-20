from pathlib import Path
from cybulde.config_schemas.raw_data_schema import RawDataConfig
from cybulde.utils.config_utils import get_config
from cybulde.utils.data_utils import initialize_dvc, initialize_dvc_storage, make_new_data_version


from cybulde.utils.utils import get_logger


@get_config(config_path="../configs", config_name="raw_data_config")
def version_data(config: RawDataConfig) -> None:
    logger = get_logger(Path(__file__).name)
    logger.info("Versioning raw data...")

    initialize_dvc()
    initialize_dvc_storage(config.dvc_remote_name, config.dvc_remote_url)
    make_new_data_version(config.dvc_raw_data_folder, config.dvc_remote_name)


if __name__ == "__main__":
    version_data()  # type: ignore
