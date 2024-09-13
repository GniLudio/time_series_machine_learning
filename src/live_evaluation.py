import argparse

import tsfel.feature_extraction
from utils import TimeLogger
import train_model
import pickle
import pylsl
import keyboard
import time
import tsfel

import tsml

def fetch_time_series():
    global time_series_inlet, time_series_buffer

    (samples, _) = time_series_inlet.pull_chunk()
    time_series_buffer.extend(samples)

def update_evaluation():
    global time_series_buffer, tsfel_configuration, model, prediction
    features = tsfel.time_series_features_extractor(
        dict_features=tsfel_configuration, 
        signal_windows=time_series_buffer,
        fs=tsml.SAMPLING_FREQUENCY,
        verbose=0,
    )
    prediction = model.predict(features)
    time_series_buffer.clear()
    print("Updated Prediction", prediction)

def on_esc():
    global exited
    exited = True

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Run the live evalution with the following parameters:")
    parser.add_argument("-i", "--input-filename", required=True, type=str, help="The input filename of the trained model.")
    parser.add_argument("-f", "--frequency", default=100, type=int, help="The evaluation interval. (in ms)")
    parser.add_argument("-d", "--domain", default="all", type=str, choices=tsml.TSFEL_FEATURE_DOMAINS, help="The tsfel domain to be used. (all if omitted)")
    parser.add_argument("-ws", "--window-size", default=100, type=int, help="The window size. (in ms)")
    args = parser.parse_args()

    start_end_logger = TimeLogger(f"live_evaluation.py\tStart\t{args}", "live_evaluation.py\tDone\t{duration:0.2f}")
    start_end_logger.start()

    # Parameters
    input_filename = args.input_filename
    frequency = args.frequency
    domain = args.domain
    window_size = args.window_size

    tsfel_configuration = tsfel.get_features_by_domain(domain != "all" and domain or None)

    with TimeLogger("Load Model", "Done\t{duration:.2f}", separator="\t"):
        with open(train_model.get_filename(input_filename), 'rb') as file:
            model = pickle.load(file)

    with TimeLogger("Setup OpenSignals Stream"	, "Done\t{duration:.2f}", separator="\t"):
        time_series_stream_info = next((stream_info for stream_info in pylsl.resolve_streams() if stream_info.name() == "OpenSignals"), None)
        time_series_inlet = time_series_stream_info is not None and pylsl.StreamInlet(time_series_stream_info) or None
        time_series_buffer: list[list[float]] = []

    # Main Loop
    prediction = 0
    last_evaluation_time = 0
    exited = False
    keyboard.hook(lambda _: on_esc())
    while not exited:
        fetch_time_series()
        if time.time() - last_evaluation_time > frequency / 1000:
            last_evaluation_time = time.time()
            update_evaluation()
        time.sleep(0)


    start_end_logger.end()