from extract_features import get_features_filename
from utils import TimeLogger
from argparse import ArgumentParser
import tsml
import os
import pandas
from sklearn.model_selection import cross_val_predict
import models

def get_cross_validation_filename(domain: tsml.TsfelFeatureDomain, window_size: int, window_overlap: int, model: str, channels: list[str], person_dependent: bool, features: list[str]):
    return os.path.join(
        person_dependent and tsml.CROSS_VALIDATION_PERSON_DEPENDENT_DIRECTORY or tsml.CROSS_VALIDATION_PERSON_INDEPENDENT_DIRECTORY,
        f"cv{person_dependent and 'p' or 'i'}-d_{domain}-f_{len(features) == len(tsml.TSFEL_FEATURES) and 'all' or '.'.join(features)}-ws_{window_size}-wo_{window_overlap}-m_{model}-c_{'.'.join(channels)}.csv"
    )

if __name__ == '__main__':
    # Parameter Parser
    parser = ArgumentParser(description = "Run a cross validation with the following parameters.")
    parser.add_argument("-d", "--domain", default="all", type=str, choices=tsml.TSFEL_FEATURE_DOMAINS, help="The tsfel feature domain to be used.")
    parser.add_argument("-f", "--feature", action="append", default=tsml.TSFEL_FEATURES, choices=tsml.TSFEL_FEATURES, help="The tsfel features to be used. (all if omitted)")
    parser.add_argument("-ws", "--window_size", default=100, type=int, help="The window size to be used. (in ms)")
    parser.add_argument("-wo", "--window_overlap", default=0, type=int, help="The window overlap to be used.")
    parser.add_argument("-m", "--model", default="RandomForestClassifier", choices=models.MODELS.keys(), help="The model to be used.")
    parser.add_argument("-c", "--channel", default=tsml.CHANNELS, action="append", choices=tsml.CHANNELS, type=str, help="The channels to be used. (all if omitted)")
    parser.add_argument("-pd", "--person_dependent", action="store_true", help="Whether to do a person-dependent cross-validation. (person-independent if omitted)")
    # TODO: Add grouping parameter
    args = parser.parse_args()
    if len(args.channel)>len(tsml.CHANNELS):
        args.channel = args.channel[len(tsml.CHANNELS):]
    if len(args.feature)>len(tsml.TSFEL_FEATURES):
        args.feature = args.feature[len(tsml.TSFEL_FEATURES):]

    # Start
    start_end_logger = TimeLogger(f"cross_validation.py\tStart\t{args}", "cross_validation.py\tDone\t{duration:.2f}")
    start_end_logger.start()

    # Parameters
    domain: tsml.TsfelFeatureDomain = args.domain
    features: str = args.feature
    window_size: int = args.window_size
    window_overlap: int = args.window_overlap
    model: str = args.model
    channels: list[tsml.Channel] = args.channel
    person_dependent: bool = args.person_dependent
    
    # Paths
    input_filename: str = get_features_filename(domain=domain, window_size=window_size, window_overlap=window_overlap)
    output_filename: str = get_cross_validation_filename(
        domain=domain,
        window_size=window_size,
        window_overlap=window_overlap,
        model=model,
        channels=channels,
        person_dependent=person_dependent,
        features=features
    )
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    # Load Features
    with TimeLogger("Loading Features".ljust(20), "Done\t{duration:.2f}", separator="\t"):
        df: pandas.DataFrame = pandas.read_csv(input_filename, index_col=False)
        additional_info = df[tsml.ADDITIONAL_COLUMNS]
        labels = df[tsml.LABEL_COLUMN]
        df.drop(columns=tsml.ADDITIONAL_COLUMNS, inplace=True)
        df.drop(columns=[column for column in df.columns if not any(column.startswith(channel) for channel in channels)], inplace=True)
        df.drop(columns=[column for column in df.columns if not any(f"_{feature}" in column for feature in features)], inplace=True)
        if df.empty:
            print("Empty dataframe", end="\t")
            exit()
        

    # Split Data for person-dependent or person-indepent
    if person_dependent:
        splits = additional_info.groupby(by=tsml.PARTICIPANT_COLUMN, as_index=True).groups
    else:
        splits = {'all': additional_info.index}

    # Cross Validation
    with TimeLogger("Cross validating".ljust(20) + "\t'" + output_filename + "'", "Done\t{duration:.2f}"):
        estimator = models.MODELS[model]()
        for i, (split_name, split_index) in enumerate(splits.items(), start=1):
            with TimeLogger("\t" + f"{i} / {len(splits)}\t{split_name}".ljust(10), "Done\t{duration:.2f}", separator="\t"):
                split_features = df.iloc[split_index]
                split_labels = labels.iloc[split_index]

                split_results = pandas.DataFrame(additional_info.iloc[split_index])
                split_results['Prediction'] = cross_val_predict(
                    estimator = estimator,
                    X = split_features,
                    y = split_labels,
                )
                split_results.to_csv(path_or_buf=output_filename, index=False, header=(i==1), mode=(i==1) and 'w' or 'a')

    # Log End
    start_end_logger.end()