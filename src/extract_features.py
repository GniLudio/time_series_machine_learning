import tsml
import pandas
from utils import TimeLogger, join_filename_parts
from argparse import ArgumentParser
import tsfel
import os

def load_dataset() -> pandas.DataFrame:
    df = pandas.DataFrame()

    for filename in os.listdir(tsml.RECORDING_TIMESERIES_DIRECTORY):
        participant = not filename.startswith("Laycee") and filename[4:-6] or filename[18+4:-6]
        print("\t", participant, filename, flush=True)

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
        df_file["Word Index"] = None
        for i in range(0, len(df_file)):
            if word_start is None:
                if df_file.loc[i, tsml.LABEL_COLUMN] != 0:
                    word_start = i
            else:
                if i == len(df_file)-1 or df_file.loc[i+1, tsml.LABEL_COLUMN] != df_file.loc[word_start, tsml.LABEL_COLUMN]:
                    #if participant == "01" and word_index in [1]:
                    #    pass
                    #elif participant == "05" and word_index in [31, 32]:
                    #    pass
                    #elif participant == "28" and word_index in [121, 122]:
                    #    pass
                    #else:
                    if i-word_start < 3900 or i-word_start > 4100:
                        print(f"\tIndex: {word_index}\tStart: {str.ljust(str(word_start+61), 7)}\tEnd: {str.ljust(str(i+61), 7)}\tLength: {str.ljust(str(i-word_start), 7)}")
                    else:
                        pass #print(f"\t{df_file.loc[word_start]['Label']}")
                    
                    if participant == "01":
                        df_file.loc[word_start:i, 'Word Index'] = word_index-1
                    else:
                        df_file.loc[word_start:i, 'Word Index'] = word_index

                    word_start = None
                    word_index += 1
        df_file = df_file[df_file['Word Index'].notna()]
        print(f"\tWord Count: {len(df_file['Word Index'].unique())}")
        df_file["Participant"] = participant
        df = pandas.concat([df, df_file])
    return df

if __name__ == '__main__':
    # Parameter Parser
    parser = ArgumentParser(description = "Extract features with the following parameters.")
    parser.add_argument("-d", "--domain", default="all", type=str, choices=tsml.TSFEL_FEATURE_DOMAINS, help="The tsfel feature domain to be used.")
    parser.add_argument("-ws", "--window_size", default=100, type=int, help="The window size to be used. (in ms)")
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
    print(dataset)
    exit()

    # group data
    with TimeLogger(start_message="Grouping Data".ljust(20), end_message="Done\t{duration:.2f}", separator="\t"):
        grouped_data = dataset.groupby(by=tsml.ADDITIONAL_COLUMNS, sort=True).groups
    
    # Extract Features
    with TimeLogger(start_message="Extract Features", end_message="Extracting Features\tDone\t{duration:.2f}"):
        configuration = tsfel.get_features_by_domain(domain != 'all' and domain or None)
        for i, (group_key, group_indices) in enumerate(grouped_data.items(), start=1):
            with TimeLogger(f"\t{str(i).rjust(len(str(len(grouped_data))))} / {str(len(grouped_data))}\t{group_key}".ljust(45), "Done\t{duration:.2f}", separator="\t"):
                features = tsfel.time_series_features_extractor(
                    config = configuration,
                    timeseries = dataset.iloc[group_indices][tsml.CHANNELS],
                    fs = tsml.SAMPLING_FREQUENCY,
                    window_size = window_size,
                    overlap = window_overlap / 100,
                    verbose = 0,
                )
                features[tsml.ADDITIONAL_COLUMNS] = group_key
                features.to_csv(path_or_buf=output_filename, mode=(i==1) and 'w' or 'a', header=(i==1), index=False)

    # End
    start_end_logger.end()