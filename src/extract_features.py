import os
from argparse import ArgumentParser

import pandas
import tsfel
import tsfel.feature_extraction.calc_features

import tsml
import utils


def get_output_filename(
    domain: tsml.TsfelFeatureDomain,
    window_size: int | None,
    window_overlap: int,
) -> str:
    return (
        os.path.join(
            tsml.FEATURES_DIRECTORY,
            utils.join_filename_parts(
                {
                    "do": domain,
                    "ws": window_size or "all",
                    "wo": window_overlap,
                }
            ),
        )
        + ".csv"
    )


def load_dataset() -> pandas.DataFrame:
    df = pandas.DataFrame()

    for filename in os.listdir(tsml.RECORDING_TIMESERIES_DIRECTORY):
        df = pandas.concat(
            [
                df,
                pandas.read_csv(
                    filepath_or_buffer=os.path.join(
                        tsml.RECORDING_TIMESERIES_DIRECTORY, filename
                    ),
                    index_col=False,
                    dtype=tsml.DATASET_DTYPE,
                ),
            ]
        )
    return df


if __name__ == "__main__":
    # Parameter Parser
    parser = ArgumentParser(
        description="Extract features with the following parameters."
    )
    parser.add_argument(
        "-d",
        "--domain",
        default="all",
        type=str,
        choices=tsml.TSFEL_FEATURE_DOMAINS,
        help="The tsfel feature domain to be used.",
    )
    parser.add_argument(
        "-ws",
        "--window_size",
        default=None,
        type=int,
        help="The window size to be used. (in ms)",
    )
    parser.add_argument(
        "-wo",
        "--window_overlap",
        default=0,
        type=int,
        help="The window overlap to be used.",
    )
    args = parser.parse_args()

    # Start
    start_end_logger = utils.TimeLogger(
        f"extract_features.py\tStart\t{args}",
        "extract_features.py\tDone\t{duration:.2f}",
    )
    start_end_logger.start()

    # Parameters
    domain: tsml.TsfelFeatureDomain = args.domain
    window_size: int = args.window_size
    window_overlap: int = args.window_overlap

    # Paths
    output_filename: str = get_output_filename(
        domain=domain,
        window_size=window_size,
        window_overlap=window_overlap,
    )
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    # Load Dataset
    with utils.TimeLogger(
        start_message="Loading Dataset".ljust(20), end_message="Done\t{duration:.2f}"
    ):
        dataset = load_dataset()

    # group data
    with utils.TimeLogger(
        start_message="Grouping Data".ljust(20),
        end_message="Done\t{duration:.2f}",
        separator="\t",
    ):
        groups = dataset.groupby(by=tsml.ADDITIONAL_COLUMNS, sort=True).groups

    # Extract Features
    with utils.TimeLogger(
        start_message="Extracting Features",
        end_message="Extracting Features\tDone\t"
        + output_filename
        + "\t{duration:.2f}",
    ):
        configuration = tsfel.get_features_by_domain(domain != "all" and domain or None)
        for i, (group_key, group_indices) in enumerate(groups.items(), start=1):
            with utils.TimeLogger(
                f"\t{str(i).rjust(len(str(len(groups))))} / {str(len(groups))}\t{group_key}".ljust(
                    45
                ),
                "Done\t{duration:.2f}",
                separator="\t",
            ):
                group_data = dataset.iloc[group_indices][tsml.CHANNELS]
                features = tsfel.feature_extraction.calc_features.time_series_features_extractor(
                    config=configuration,
                    timeseries=group_data,
                    fs=tsml.SAMPLING_FREQUENCY,
                    window_size=window_size,
                    overlap=window_overlap / 100,
                    verbose=0,
                )
                features[tsml.ADDITIONAL_COLUMNS] = group_key
                features.to_csv(
                    path_or_buf=output_filename,
                    mode=(i == 1) and "w" or "a",
                    header=(i == 1),
                    index=False,
                )

    # End
    start_end_logger.end()
