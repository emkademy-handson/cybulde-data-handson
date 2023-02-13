import os
from pathlib import Path

from dask.distributed import Client
import dask.dataframe as dd

from cybulde.config_schemas.data_processing_schema import DataProcessingConfig
from hydra.utils import instantiate
from cybulde.data_processing.dataset_cleaners import DatasetCleanerManager

from cybulde.utils.config_utils import get_config
from cybulde.utils.utils import get_logger


def process_raw_data(df_partition: dd.core.DataFrame, dataset_cleaner_manager: DatasetCleanerManager) -> dd.core.DataFrame:
    return df_partition["text"].apply(dataset_cleaner_manager)


@get_config(config_path="../configs", config_name="data_processing_config")
def process_data(config: DataProcessingConfig) -> None:
    logger = get_logger(Path(__file__).name)
    logger.info("Processing raw data...")

    processed_data_save_dir = config.processed_data_save_dir
    Path(processed_data_save_dir).mkdir(parents=True, exist_ok=True)

    cluster = instantiate(config.dask_cluster)
    client = Client(cluster)

    try:
        dataset_reader_manager = instantiate(config.dataset_reader_manager)
        dataset_cleaner_manager = instantiate(config.dataset_cleaner_manager)

        df = dataset_reader_manager.read_data(nrof_workers=config.dask_cluster.n_workers)
        print(f"{df.npartitions=}")

        logger.info("Starting cleaning...")
        df = df.assign(cleaned_text=df.map_partitions(process_raw_data, dataset_cleaner_manager=dataset_cleaner_manager, meta=("text", "object")))

        df = df.compute()

        train_df_path = os.path.join(processed_data_save_dir, "train.parquet")
        dev_df_path = os.path.join(processed_data_save_dir, "dev.parquet")
        test_df_path = os.path.join(processed_data_save_dir, "test.parquet")

        df[df["set"] == "train"].to_parquet(train_df_path) 
        df[df["set"] == "dev"].to_parquet(dev_df_path) 
        df[df["set"] == "test"].to_parquet(test_df_path) 

        logger.info("Done!")

    finally:
        logger.info("Closing cluster...")
        client.close()
        cluster.close()


if __name__ == "__main__":
    process_data()
