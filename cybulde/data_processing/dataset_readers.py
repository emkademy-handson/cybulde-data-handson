import os
from abc import ABC, abstractmethod
from typing import Optional

import dask.dataframe as dd
from dask_ml.model_selection import train_test_split

from cybulde.utils.utils import get_logger


class DatasetReader(ABC):
    required_columns = {"text", "label", "set", "dataset_name"}
    set_names = {"train", "dev", "test"}

    def __init__(self, dataset_dir: str, dev_set_ratio: float, test_set_ratio: float, dataset_name: str) -> None:
        super().__init__()
        self.logger = get_logger(self.__class__.__name__)
        self.dataset_dir = dataset_dir
        self.dev_set_ratio = dev_set_ratio
        self.test_set_ratio = test_set_ratio
        self.dataset_name = dataset_name

    def read_data(self) -> dd.core.DataFrame:
        train_df, dev_df, test_df = self._read_data()
        df = self.assign_set_names_to_data_frames_and_merge(train_df, dev_df, test_df)
        df["dataset_name"] = self.dataset_name
        if any(required_column not in df.columns.values for required_column in self.required_columns):
            raise RuntimeError(f"{self.__class__.__name__}._read_data method should return a DataFrame with columns: {self.required_columns}")
        unique_set_values = set(df["set"].unique().compute().tolist())
        if unique_set_values != self.set_names:
            raise RuntimeError(f"Value of 'set' column can only be one of: {self.set_names}")
        df = df[list(self.required_columns)]
        return df
 
    @abstractmethod
    def _read_data(self) -> tuple[dd.core.DataFrame, dd.core.DataFrame, dd.core.DataFrame]:
        """
        Read and split dataset into 3 sets: train, dev, test.
        The return value must be a dd.core.DataFrame, with required columns: self.required_columns
        """

    def split_dataset(self, df: dd.core.DataFrame, test_size: float, stratify_column: Optional[str] = None) -> tuple[dd.core.DataFrame, dd.core.DataFrame]:
        if stratify_column is None:
            return train_test_split(df, test_size=test_size, random_state=1234, shuffle=True)  # type: ignore
        unique_column_values = df[stratify_column].unique()
        first_dfs = []
        second_dfs = []
        for unique_set_values in unique_column_values:
            sub_df = df[df[stratify_column] == unique_set_values]
            sub_first_df, sub_second_df = train_test_split(sub_df, test_size=test_size, random_state=1234, shuffle=True)
            first_dfs.append(sub_first_df)
            second_dfs.append(sub_second_df)

        first_df = dd.concat((first_dfs))  # type: ignore
        second_df = dd.concat((second_dfs))  # type: ignore

        return first_df, second_df

    def assign_set_names_to_data_frames_and_merge(self, train_df: dd.core.DataFrame, dev_df: dd.core.DataFrame, test_df: dd.core.DataFrame) -> dd.core.DataFrame:
        train_df["set"] = "train"
        dev_df["set"] = "dev"
        test_df["set"] = "test"
        return dd.concat([train_df, dev_df, test_df])


class GHCDatasetReader(DatasetReader):
    def _read_data(self) -> dd.core.DataFrame:
        self.logger.info("Reading GHC data...")
        train_df = dd.read_csv(os.path.join(self.dataset_dir, "ghc_train.tsv"), sep="\t", header=0)
        test_df = dd.read_csv(os.path.join(self.dataset_dir, "ghc_test.tsv"), sep="\t", header=0)

        train_df["label"] = (train_df["hd"] + train_df["cv"] + train_df["vo"] > 0).astype(int)
        test_df["label"] = (test_df["hd"] + test_df["cv"] + test_df["vo"] > 0).astype(int)

        train_df, dev_df = self.split_dataset(train_df, self.dev_set_ratio, stratify_column="label")
        return train_df, dev_df, test_df


class JigsawToxicCommentsDatasetReader(DatasetReader):
    def __init__(self, dataset_dir: str, dev_set_ratio: float, test_set_ratio: float, dataset_name: str) -> None:
        super().__init__(dataset_dir, dev_set_ratio, test_set_ratio, dataset_name)
        self.columns_for_label = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]

    def _read_data(self) -> dd.core.DataFrame:
        self.logger.info("Reading JigsawToxicComments data...")
        test_df = self.merge_test_data_and_labels()
        test_df = self.filter_not_used_rows_from_test_data_frame(test_df)
        test_df = self.get_text_and_label_columns(test_df)

        train_df = dd.read_csv(os.path.join(self.dataset_dir, "train.csv"))
        train_df = self.get_text_and_label_columns(train_df)

        train_df, dev_df = self.split_dataset(train_df, self.dev_set_ratio, stratify_column="label")
        return train_df, dev_df, test_df

    def merge_test_data_and_labels(self) -> dd.core.DataFrame:
        test_df = dd.read_csv(os.path.join(self.dataset_dir, "test.csv"))
        test_labels_df = dd.read_csv(os.path.join(self.dataset_dir, "test_labels.csv"))
        test_df = test_df.merge(test_labels_df, on=["id"])
        return test_df

    def filter_not_used_rows_from_test_data_frame(self, test_df: dd.core.DataFrame) -> dd.core.DataFrame:
        test_df = test_df[test_df["toxic"]!=-1]
        return test_df

    def get_text_and_label_columns(self, df: dd.core.DataFrame) -> dd.core.DataFrame:
        df["label"] = (df[self.columns_for_label].sum(axis=1) > 0).astype(int)
        df_renamed = df.rename(columns={"comment_text": "text"})
        return df_renamed[["text", "label"]]


class TwitterDatasetReader(DatasetReader):
    def _read_data(self) -> dd.core.DataFrame:
        self.logger.info("Reading Twitter data...")
        df = dd.read_csv(os.path.join(self.dataset_dir, "cyberbullying_tweets.csv"))
        df = df.rename(columns={"tweet_text": "text", "cyberbullying_type": "label"})
        df["label"] = (df["label"] != "not_cyberbullying").astype(int)

        train_df, test_df = self.split_dataset(df, self.test_set_ratio, "label")
        train_df, dev_df = self.split_dataset(train_df, self.dev_set_ratio, "label")
        return train_df, dev_df, test_df


class DatasetReaderManager:
    def __init__(self, dataset_readers: dict[str, DatasetReader]) -> None:
        self.dataset_readers = dataset_readers

    def read_data(self) -> dd.core.DataFrame:
        dfs = [dataset_reader.read_data() for dataset_reader in self.dataset_readers.values()]
        df = dd.concat(dfs)
        return df
        
