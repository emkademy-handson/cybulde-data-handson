from pathlib import Path
from subprocess import CalledProcessError

from cybulde.utils.utils import get_logger, run_shell_command

DATA_UTILS_LOGGER = get_logger(Path(__file__).name)


def is_dvc_initialized() -> bool:
    return (Path().cwd() / ".dvc").exists()


def initialize_dvc() -> None:
    if is_dvc_initialized():
        DATA_UTILS_LOGGER.info("DVC is already initialized...")
        return
    run_shell_command("dvc init")
    run_shell_command("dvc config core.analytics false")
    run_shell_command("dvc config core.autostage true")
    run_shell_command("git add .dvc")
    run_shell_command("git commit -nm 'Initialized DVC'")


def initialize_dvc_storage(dvc_remote_name: str, dvc_remote_url: str) -> None:
    if not run_shell_command("dvc remote list"):
        run_shell_command(f"dvc remote add -d {dvc_remote_name} {dvc_remote_url}")
        run_shell_command("git add .dvc/config")
        run_shell_command(f"git commit -nm 'Configured remote storage at: {dvc_remote_url}'")
    else:
        DATA_UTILS_LOGGER.info("DVC storage is already initialized...")


def make_new_data_version(dvc_raw_data_folder: str, dvc_remote_name: str) -> None:
    try:
        status = run_shell_command(f"dvc status {dvc_raw_data_folder}.dvc")
        if status == "Data and pipelines are up to date.\n":
            DATA_UTILS_LOGGER.info("Data and pipelines are up to date.")
            return
        commit_to_dvc(dvc_raw_data_folder, dvc_remote_name)
    except CalledProcessError:
        commit_to_dvc(dvc_raw_data_folder, dvc_remote_name)


def commit_to_dvc(dvc_raw_data_folder: str, dvc_remote_name: str) -> None:
    current_version = run_shell_command("git tag --list | sort -t v -k 2 -g | tail -1 | sed 's/v//'")
    if not current_version:
        current_version = "0"
    next_version = f"v{int(current_version)+1}"
    run_shell_command(f"dvc add {dvc_raw_data_folder}")
    run_shell_command("git add .")
    run_shell_command(f"git commit -nm 'Updated version of the data from v{current_version} to {next_version}'")
    run_shell_command(f"git tag -a {next_version} -m 'Data version {next_version}'")
    run_shell_command(f"dvc push {dvc_raw_data_folder}.dvc --remote {dvc_remote_name}")
    run_shell_command("git push --follow-tags")
    run_shell_command("git push -f --tags")


def get_cmd_to_get_raw_data(
    version: str,
    raw_data_local_save_dir: str,
    dvc_raw_data_remote_repo: str,
    dvc_raw_data_folder: str,
    github_user_name: str,
    github_access_token: str,
) -> str:
    """Get shell command to download the raw data from dvc store

    Parameters:
    -----------
    version: str
        data version
    raw_data_local_save_dir: str
        where to save the downloaded data
    dvc_raw_data_remote_repo: str
        DVC repositroy that holds information about the data
    dvc_raw_data_folder: str
        location where the remote data is stored
    github_user_name: str
        github user name
    github_access_token: str
        github access token

    Returns
    -------
    str
        shell command to download raw data from DVC
    """
    raw_data_local_save_dir_path = Path(raw_data_local_save_dir)

    if raw_data_local_save_dir_path.exists():
        dvc_file = f"{raw_data_local_save_dir}{Path(dvc_raw_data_folder).name}.dvc"
        cmd = f"dvc update {dvc_file} --rev {version}"
    else:
        raw_data_local_save_dir_path.mkdir(parents=True, exist_ok=True)
        without_https = dvc_raw_data_remote_repo.replace("https://", "") 
        dvc_remote_repo = f"https://{github_user_name}:{github_access_token}@{without_https}"
        cmd = f"dvc import {dvc_remote_repo} {dvc_raw_data_folder} --rev {version} -o {raw_data_local_save_dir}" 
    return cmd
