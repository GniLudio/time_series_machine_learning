import os

import pandas

import tsml
from utils import TimeLogger

INDEX_COLUMN = "Word Index"

if __name__ == "__main__":
    os.makedirs(tsml.WORD_STUDY_DIRECTORY_PREPROCESSED, exist_ok=True)

    start_end_logger = TimeLogger("proprocess_dataset.py\tStart", "preprocess_dataset.py\tDone\t{duration:.2f}")
    start_end_logger.start()

    for filename in os.listdir(tsml.WORD_STUDY_DIRECTORY_RAW):
        if filename.startswith("_"):
            continue
        print(f"\t{filename}")

        with TimeLogger("\tLoading Data", "Done\t{duration:.2f}", separator="\t"):
            df = pandas.read_csv(
                os.path.join(tsml.WORD_STUDY_DIRECTORY_RAW, filename),
                sep="\t",
                index_col=False,
                dtype=tsml.DATASET_DTYPE,
            )
        with TimeLogger("\tDropping Columns", "Done\t{duration:.2f}", separator="\t"):
            df.drop(
                columns=[c for c in df.columns if c not in tsml.DATASET_DTYPE.keys()],
                inplace=True,
            )

        with TimeLogger("\tAdding Word Indices", "Done\t{duration:.2f}"):
            df[INDEX_COLUMN] = pandas.Series(dtype=pandas.Int64Dtype())
            word_index = 0
            word_start_row = None
            for i in range(len(df)):
                row = df.loc[i]
                if word_start_row is None:
                    # looking for start of word
                    if df.iloc[i][tsml.LABEL_COLUMN] != 0:
                        print(
                            f"\t\t{str(word_index).ljust(3)}\t{str(i).ljust(7)}",
                            end="\t",
                        )
                        word_start_row = i
                else:
                    # looking for end of word
                    if i == len(df) or df.iloc[i + 1][tsml.LABEL_COLUMN] == 0:
                        print(f"{str(i).ljust(7)}\t{str(i-word_start_row).ljust(4)}\t{row[tsml.LABEL_COLUMN]}")
                        df.loc[pandas.RangeIndex(word_start_row, i), INDEX_COLUMN] = word_index
                        word_index += 1
                        word_start_row = None

        with TimeLogger("Saving", "Done", separator="\t"):
            df = df.loc[df[INDEX_COLUMN].notnull()]
            df["Participant"] = filename[:-4]
            df.to_csv(
                os.path.join(tsml.WORD_STUDY_DIRECTORY_PREPROCESSED, filename[:-4] + ".csv"),
                index=False,
            )

    start_end_logger.end()
