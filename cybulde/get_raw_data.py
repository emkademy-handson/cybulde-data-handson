from pathlib import Path

from cybulde.config_schemas.raw_data_schema import RawDataConfig
from cybulde.utils.config_utils import get_config
from cybulde.utils.data_utils import get_cmd_to_get_raw_data
from cybulde.utils.gcp_utils import access_secret_version
from cybulde.utils.utils import get_logger, run_shell_command


@get_config(config_path="../configs", config_name="raw_data_config")
def get_raw_data(config: RawDataConfig) -> None:
    logger = get_logger(Path(__file__).name)
    logger.info("Getting raw data...")

    logger.info(f"Getting secret with name: {config.github_access_token_secret_id}")
    github_access_token = access_secret_version(
        config.infrastructure.project_id, 
        config.github_access_token_secret_id
    )

    cmd_to_get_raw_data = get_cmd_to_get_raw_data(
        version=config.version,
        raw_data_local_save_dir=config.raw_data_local_save_dir,
        dvc_raw_data_remote_repo=config.dvc_raw_data_remote_repo,
        dvc_raw_data_folder=config.dvc_raw_data_folder,
        github_user_name=config.github_user_name,
        github_access_token=github_access_token
    )

    Path(config.raw_data_local_save_dir).mkdir(parents=True, exist_ok=True)

    logger.info("Running command to get raw data...")
    run_shell_command(cmd_to_get_raw_data)

    logger.info("Syncing GCS bucket with raw data...")
    run_shell_command(f"gsutil -m rsync -d -r {config.raw_data_local_save_dir} {config.raw_data_gcs_location}")

if __name__ == "__main__":
    get_raw_data()
