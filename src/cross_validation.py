import pandas.api.typing
from utils import TimeLogger, join_filename_parts
from argparse import ArgumentParser
import tsml
import os
import pandas
from sklearn.model_selection import cross_val_predict
import models

def load_familiarities() -> pandas.api.typing.DataFrameGroupBy:
    return pandas.read_excel(io = os.path.join("data", "EMT_cor3.xlsx"), usecols=['participant', 'trial', 'familiarity']).groupby(['participant', 'trial'])

if __name__ == '__main__':
    # Parameter Parser
    parser = ArgumentParser(description = "Run a cross validation with the following parameters.")
    parser.add_argument("-d", "--domain", default="all", type=str, choices=tsml.TSFEL_FEATURE_DOMAINS, help="The tsfel feature domain to be used.")
    parser.add_argument("-ws", "--window_size", default=None, type=int, help="The window size to be used. (in ms)")
    parser.add_argument("-wo", "--window_overlap", default=0, type=int, help="The window overlap to be used.")
    parser.add_argument("-m", "--model", default="RandomForestClassifier", choices=models.MODELS.keys(), help="The model to be used.")
    parser.add_argument("-c", "--channel", action="append", choices=tsml.CHANNELS, type=str, help="The channels to be used. (all if omitted)")
    parser.add_argument("-pd", "--person_dependent", action="store_true", help="Whether to do a person-dependent cross-validation. (person-independent if omitted)")
    parser.add_argument("-fa", "--familiarity", type=str, choices=["yes", "no"], help="Limits the data to one familiarity.")
    args = parser.parse_args()

    # Start
    start_end_logger = TimeLogger(f"cross_validation.py\tStart\t{args}", "cross_validation.py\tDone\t{duration:.2f}")
    start_end_logger.start()

    # Parameters
    domain: tsml.TsfelFeatureDomain = args.domain
    window_size: int = args.window_size
    window_overlap: int = args.window_overlap
    model: str = args.model
    channels: list[tsml.Channel] = args.channel
    person_dependent: bool = args.person_dependent
    familiarity: str | None = args.familiarity
    
    # Paths
    input_filename: str = os.path.join(
        tsml.FEATURES_DIRECTORY,
        join_filename_parts({
            'do': domain,
            'ws': window_size or 'all',
            'wo': window_overlap
        }) + ".csv"
    )
    output_filename = os.path.join(
        person_dependent and tsml.CROSS_VALIDATION_PERSON_DEPENDENT_DIRECTORY or tsml.CROSS_VALIDATION_PERSON_INDEPENDENT_DIRECTORY,
        (person_dependent and 'cvp_' or 'cvi_') +
        join_filename_parts({
            'do': domain,
            'ws': window_size or 'all',
            'wo': window_overlap,
            'mo': model,
            'ch': channels and ".".join(channels) or "all",
            'pd': person_dependent and 'yes' or 'no'
        }) + ".csv"
    )
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    # Load Features
    with TimeLogger("Loading Features".ljust(20), "Done\t{duration:.2f}", separator="\t"):
        df: pandas.DataFrame = pandas.read_csv(input_filename, index_col=False)
        
        familiarities = load_familiarities()
        df['Familiarity'] = df.apply(lambda row: str(familiarities.get_group((int(row[tsml.PARTICIPANT_COLUMN]), int(row[tsml.TRIAL_COLUMN])))['familiarity'].values[0]), axis=1)
        if familiarity:
            df = df[df['Familiarity'] == familiarity]
            df.reset_index(inplace=True)
        
        additional_info = df[tsml.ADDITIONAL_COLUMNS]
        df.drop(columns=tsml.ADDITIONAL_COLUMNS, inplace=True)
        
        if channels:
            df.drop(columns=[column for column in df.columns if not any(column.startswith(channel) for channel in channels)], inplace=True)
        
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
            with TimeLogger("\t" + f"{i} / {len(splits)}".ljust(10), "Done\t{duration:.2f}", separator="\t"):
                split_features = df.iloc[split_index]
                split_labels = additional_info[tsml.LABEL_COLUMN].iloc[split_index]

                split_results = pandas.DataFrame(additional_info.iloc[split_index])
                split_results['Prediction'] = cross_val_predict(
                    estimator = estimator,
                    X = split_features,
                    y = split_labels,
                )
                split_results.to_csv(path_or_buf=output_filename, index=False, header=(i==1), mode=(i==1) and 'w' or 'a')

    # Log End
    start_end_logger.end()