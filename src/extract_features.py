import tsml
import pandas
from utils import TimeLogger, join_filename_parts
from argparse import ArgumentParser
import tsfel, tsfel.feature_extraction.calc_features
import os

def load_dataset() -> pandas.DataFrame:
    df = pandas.DataFrame()

    for filename in sorted(os.listdir(tsml.RECORDING_TIMESERIES_DIRECTORY)[:1]):
        participant = not filename.startswith("Laycee") and filename[4:-6] or filename[18+4:-6]
        print("\t", participant, flush=True)

        df_file = pandas.read_csv(
            filepath_or_buffer=os.path.join(tsml.RECORDING_TIMESERIES_DIRECTORY, filename), 
            index_col=False, 
            dtype=tsml.DATASET_DTYPE,
            header=participant != "49" and 59 or 60, # data for participant 49 has an additional header line
            sep="\t",
            usecols = [1, 2, 3, 4, 5, 27],
            names = ["CH1","CH2","CH3","CH4","CH5", "Label"]
        )
        word_index = 1
        word_start = None
        df_file["Trial"] = None
        for i in range(0, len(df_file)):
            if word_start is None:
                if df_file.loc[i, tsml.LABEL_COLUMN] != 0:
                    word_start = i
            else:
                if i == len(df_file)-1 or df_file.loc[i+1, tsml.LABEL_COLUMN] != df_file.loc[word_start, tsml.LABEL_COLUMN]:
                    # get actual word index
                    actual_word_index = word_index
                    if participant == "01":
                        if word_index in [1]:
                            actual_word_index = None
                        else:
                            actual_word_index = word_index -1
                    elif participant == "05" and word_index in [31, 32]:
                        actual_word_index = None
                    elif participant == "28" and word_index in [121, 122]:
                        actual_word_index = None
                    elif participant == "46":
                        if word_index in [1, 2, 3, 4]:
                            actual_word_index = None
                        else:
                            actual_word_index -= 4
                    elif participant == "50":
                        if word_index in [1,2,3,4,5,6]:
                            actual_word_index = None
                        else:
                            actual_word_index -= 6 

                    if actual_word_index is not None:
                        print(f"\t\t{actual_word_index}\t{df_file.loc[word_start]['Label']}")
                    else:
                        print(f"\t\t----{word_index}\t{df_file.loc[word_start]['Label']}")

                    if actual_word_index is not None:
                        if i-word_start < 3900 or i-word_start > 4100:
                            print(f"\t\t\t----LENGTH - Start: {str.ljust(str(word_start+61), 7)}\tEnd: {str.ljust(str(i+61), 7)}\tLength: {str.ljust(str(i-word_start), 7)}")
                        else:
                            df_file.loc[word_start:i, 'Trial'] = actual_word_index

                    word_start = None
                    word_index += 1
        df_file = df_file[df_file['Trial'].notna()]
        df_file["Participant"] = participant
        df = pandas.concat([df, df_file])
        print(f"\tWord Count: {len(df_file['Trial'].unique())}")
    df.reset_index(inplace=True)
    return df

if __name__ == '__main__':
    # Parameter Parser
    parser = ArgumentParser(description = "Extract features with the following parameters.")
    parser.add_argument("-d", "--domain", default="all", type=str, choices=tsml.TSFEL_FEATURE_DOMAINS, help="The tsfel feature domain to be used.")
    parser.add_argument("-ws", "--window_size", default=None, type=int, help="The window size to be used. (in ms)")
    parser.add_argument("-wo", "--window_overlap", default=0, type=int, help="The window overlap to be used.")
    args = parser.parse_args()

    # Start
    start_end_logger = TimeLogger(f"extract_features.py\tStart\t{args}", "extract_features.py\tDone\t{duration:.2f}")
    start_end_logger.start()

    # Parameters
    domain: tsml.TsfelFeatureDomain = args.domain
    window_size: int = args.window_size
    window_overlap: int = args.window_overlap
    
    # Paths
    output_filename: str = os.path.join(
        tsml.FEATURES_DIRECTORY, 
        join_filename_parts({
            'do': domain,
            'ws': window_size,
            'wo': window_overlap
        })
    ) + ".csv"
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    # Load Dataset
    with TimeLogger(start_message="Loading Dataset".ljust(20), end_message="Done\t{duration:.2f}"):
        dataset = load_dataset()

    # group data
    with TimeLogger(start_message="Grouping Data".ljust(20), end_message="Done\t{duration:.2f}", separator="\t"):
        groups = dataset.groupby(by=tsml.ADDITIONAL_COLUMNS, sort=True).groups

    # Extract Features
    with TimeLogger(start_message="Extract Features", end_message="Extracting Features\tDone\t{duration:.2f}"):
        configuration = tsfel.get_features_by_domain(domain != 'all' and domain or None)
        for i, (group_key, group_indices) in enumerate(groups.items(), start=1):
            with TimeLogger(f"\t{str(i).rjust(len(str(len(groups))))} / {str(len(groups))}\t{group_key}".ljust(45), "Done\t{duration:.2f}", separator="\t"):
                group_data = dataset.iloc[group_indices][tsml.CHANNELS]
                features = tsfel.feature_extraction.calc_features.time_series_features_extractor(
                    config = configuration,
                    timeseries = group_data,
                    fs = tsml.SAMPLING_FREQUENCY,
                    window_size = window_size or len(group_data),
                    overlap = window_overlap / 100,
                    verbose = 0,
                )
                features[tsml.ADDITIONAL_COLUMNS] = group_key
                features.to_csv(path_or_buf=output_filename, mode=(i==1) and 'w' or 'a', header=(i==1), index=False)

    # End
    start_end_logger.end()