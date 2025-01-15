import argparse
import tsml
import models
import pickle
import os
import time
import tsfel
import pylsl
import pandas

import extract_features
from utils import TimeLogger

def get_filename(filename: str):
    return os.path.join(tsml.TRAINED_MODEL_DIRECTORY, filename + ".pickle")

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Run the live evalution with the following parameters:")
    parser.add_argument("-d", "--domain", default="all", type=str, choices=tsml.TSFEL_FEATURE_DOMAINS, help="The tsfel feature domain to be used.")
    parser.add_argument("-ws", "--window_size", default=100, type=int, help="The window size to be used. (in ms)")
    parser.add_argument("-wo", "--window_overlap", default=0, type=int, help="The window overlap to be used.")
    parser.add_argument("-m", "--model", default="RandomForestClassifier", choices=models.MODELS.keys(), help="The model to be used.")
    parser.add_argument("-o", "--output-filename", type=str, required=True, help="The output filename.")
    parser.add_argument("-pa", "--participant", type=str, help="The participant.")
    args = parser.parse_args()

    start_end_logger = TimeLogger(f"train_model.py\tStart\t{args}", "train_model.py\tDone\t{duration:0.2f}")
    start_end_logger.start()

    # Parameters
    domain = args.domain
    window_size = args.window_size
    window_overlap = args.window_overlap
    model_name = args.model
    participant = args.participant
    output_filename = get_filename(args.output_filename)

    with TimeLogger("Loading Features", "Done\t{duration:.2f}", separator="\t"):
        dataset = pandas.read_csv(extract_features.get_features_filename(domain, window_size, window_overlap, participant))

    with TimeLogger("Training Model", "Done\t{duration:.2f}", separator="\t"):
        model = models.MODELS[model_name]()
        X = dataset.drop(columns=tsml.ADDITIONAL_COLUMNS, inplace=False)
        Y = dataset[tsml.LABEL_COLUMN]
        model.fit(X, Y)

    with TimeLogger("Saving", "Done\t{duration:.2f}", separator="\t"):
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
        with open(output_filename, "wb") as file:
            pickle.dump(model, file)

    start_end_logger.end()