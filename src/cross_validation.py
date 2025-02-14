import os
from argparse import ArgumentParser

import pandas
import pandas.api.typing
from sklearn.model_selection import cross_val_predict

import extract_features
import models
import tsml
import utils


def get_output_filename(
    domain: str,
    window_size: int | None,
    window_overlap: int,
    model: str,
    channels: list[str] | str | None,
    person_dependent: bool | None,
    familiarity: str | None,
):
    """Returns the filename for the results of the cross validation"""
    return os.path.join(
        tsml.CROSS_VALIDATION_DIRECTORY,
        "cv_"
        + utils.join_filename_parts(
            {
                "do": domain,
                "ws": window_size or "all",
                "wo": window_overlap,
                "mo": model,
                "ch": channels and ".".join(channels) or "all",
                "pd": person_dependent and "yes" or "no",
                "fa": familiarity or "both",
            }
        )
        + ".csv",
    )


if __name__ == "__main__":
    # Parameter Parser
    parser = ArgumentParser(
        description="Run a cross validation with the following parameters."
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
    parser.add_argument(
        "-m",
        "--model",
        default="RandomForestClassifier",
        choices=models.MODELS.keys(),
        help="The model to be used.",
    )
    parser.add_argument(
        "-c",
        "--channel",
        action="append",
        choices=tsml.CHANNELS,
        type=str,
        help="The channels to be used. (all if omitted)",
    )
    parser.add_argument(
        "-pd",
        "--person_dependent",
        action="store_true",
        help="Whether to do a person-dependent cross-validation. (person-independent if omitted)",
    )
    parser.add_argument(
        "-fa",
        "--familiarity",
        type=str,
        choices=["yes", "no", "both"],
        default="both",
        help="Limits the data to one familiarity.",
    )
    args = parser.parse_args()

    # Start
    start_end_logger = utils.TimeLogger(
        f"cross_validation.py\tStart\t{args}",
        "cross_validation.py\tDone\t{duration:.2f}",
    )
    start_end_logger.start()

    # Parameters
    domain: tsml.TsfelFeatureDomain = args.domain
    window_size: int = args.window_size
    window_overlap: int = args.window_overlap
    model: str = args.model
    channels: list[tsml.Channel] = args.channel
    person_dependent: bool = args.person_dependent
    familiarity: str = args.familiarity or "both"

    # Paths
    input_filename: str = extract_features.get_output_filename(
        domain,
        window_size,
        window_overlap,
    )
    output_filename = get_output_filename(
        domain,
        window_size,
        window_overlap,
        model,
        channels,
        person_dependent,
        familiarity,
    )
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    # Load Features
    with utils.TimeLogger(
        "Loading Features".ljust(20), "Done\t{duration:.2f}", separator="\t"
    ):
        df: pandas.DataFrame = pandas.read_csv(input_filename, index_col=False)
        if familiarity != "both":
            familiarities = utils.load_familiarities()
            df["Familiarity"] = df.apply(
                lambda row: str(
                    familiarities.get_group(
                        (int(row[tsml.PARTICIPANT_COLUMN]), int(row[tsml.TRIAL_COLUMN]))
                    )["familiarity"].values[0]
                ),
                axis=1,
            )
            df = df[df["Familiarity"] == familiarity]
            tsml.ADDITIONAL_COLUMNS.append("Familiarity")
            df.reset_index(inplace=True)

        additional_info = df[df.columns.intersection(tsml.ADDITIONAL_COLUMNS)]
        df.drop(
            columns=df.columns.intersection(tsml.ADDITIONAL_COLUMNS),
            inplace=True,
        )

        if channels:
            df.drop(
                columns=[
                    column
                    for column in df.columns
                    if not any(column.startswith(channel) for channel in channels)
                ],
                inplace=True,
            )

        if df.empty:
            print("Empty dataframe", end="\t")
            exit()

    # Split Data for person-dependent or person-indepent
    if person_dependent:
        splits = additional_info.groupby(
            by=tsml.PARTICIPANT_COLUMN, as_index=True
        ).groups
    else:
        splits = {"all": additional_info.index}

    # Cross Validation
    with utils.TimeLogger(
        "Cross validating".ljust(20) + "\t'" + output_filename + "'",
        "Done\t{duration:.2f}",
    ):
        estimator = models.MODELS[model]()
        for i, (split_name, split_index) in enumerate(splits.items(), start=1):
            with utils.TimeLogger(
                "\t" + f"{i} / {len(splits)}".ljust(10),
                "Done\t{duration:.2f}",
                separator="\t",
            ):
                split_features = df.iloc[split_index]
                split_labels: pandas.DataFrame = additional_info[
                    tsml.LABEL_COLUMN
                ].iloc[split_index]
                n_splits = split_labels.value_counts().min()
                split_additional_info: pandas.DataFrame = additional_info.iloc[
                    split_index
                ]
                split_groups = [
                    str(group) for i, group in split_additional_info.iterrows()
                ]

                split_results = pandas.DataFrame(
                    additional_info.iloc[split_index],
                )
                split_results[tsml.PREDICTION_COLUMN] = cross_val_predict(
                    estimator=estimator,
                    X=split_features,
                    y=split_labels,
                    groups=split_groups,
                    cv=n_splits < 5 and n_splits or 5,
                )
                split_results.to_csv(
                    path_or_buf=output_filename,
                    index=False,
                    header=(i == 1),
                    mode=(i == 1) and "w" or "a",
                )

    # Log End
    start_end_logger.end()
