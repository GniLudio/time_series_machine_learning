import pylsl
import argparse
import pandas
import sklearn
import sklearn.ensemble
from sklearn.datasets import make_classification
import tsml
import models
from utils import TimeLogger
from extract_features import load_features

def fetch_time_series():
    global time_series_inlet

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Run the live evalution with the following parameters:")
    parser.add_argument("-i", "--interval", default=100, type=int, help="The evaluation interval.")
    parser.add_argument("-d", "--domain", default="all", type=str, choices=tsml.TSFEL_FEATURE_DOMAINS, help="The tsfel feature domain to be used.")
    parser.add_argument("-ws", "--window_size", default=100, type=int, help="The window size to be used. (in ms)")
    parser.add_argument("-wo", "--window_overlap", default=20, type=int, help="The window overlap to be used.")
    parser.add_argument("-m", "--model", default="RandomForestClassifier", choices=models.MODELS.keys(), help="The model to be used.")
    args = parser.parse_args()

    start_end_logger = TimeLogger(f"live_evaluation.py\tStart\t{args}", "live_evaluation.py\tDone\t{duration:0.2f}")
    start_end_logger.start()

    # Parameters
    interval = args.interval
    domain = args.domain
    window_size = args.window_size
    window_overlap = args.window_overlap
    model_name = args.model

    with TimeLogger("Setup Model", "Done\t{duration:.2f}", separator="\t"):
        model: sklearn.ensemble.RandomForestClassifier = models.MODELS[model_name]()

    with TimeLogger("Loading Features", "Done\t{duration:.2f}", separator="\t"):
        dataset = load_features(domain, window_size, window_overlap)
        dataset.sample(n=len(dataset) // 10_000)

    with TimeLogger("Training Model", "Done\t{duration:.2f}", separator="\t"):
        X = dataset.drop(columns=tsml.ADDITIONAL_COLUMNS, inplace=False)
        Y = dataset[tsml.LABEL_COLUMN]
        model.fit(X, Y)

    #with TimeLogger("Setup OpenSignals Stream"	, "Done\t{duration:.2f}", separator="\t"):
    #    time_series_stream_info = next((stream_info for stream_info in pylsl.resolve_streams() if stream_info.name() == "OpenSignals"), None)
    #    time_series_inlet = time_series_stream_info is not None and pylsl.StreamInlet(time_series_stream_info) or None
    #    time_series_buffer: list[list[float]] = []

    start_end_logger.end()