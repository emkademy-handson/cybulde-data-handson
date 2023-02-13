from pathlib import Path

from cybulde.config_schemas.data_processing_schema import DataProcessingConfig
from hydra.utils import instantiate

from cybulde.utils.config_utils import get_config
from cybulde.utils.utils import get_logger


@get_config(config_path="../configs", config_name="data_processing_config")
def process_data(config: DataProcessingConfig) -> None:
    logger = get_logger(Path(__file__).name)
    logger.info("Processing raw data...")

    dataset_reader_manager = instantiate(config.dataset_reader_manager)
    dataset_cleaner_manager = instantiate(config.dataset_cleaner_manager)

    df = dataset_reader_manager.read_data()

    texts = df.compute().sample(n=5)

    for i in range(5):
        text = texts.iloc[i]["text"]
        cleaned_text = dataset_cleaner_manager(text)

        print(60*"#")
        print(f"{text=}")
        print(f"{cleaned_text=}")
        print(60*"#")

    # print(df.compute().head(10))


if __name__ == "__main__":
    process_data()
