import argparse

import tsfel.feature_extraction
from utils import TimeLogger
import train_model
import pickle
import pylsl
import keyboard
import time
import tsfel
import pandas

import tsml

def fetch_time_series():
    global time_series_inlet, time_series_buffer

    (samples, _) = time_series_inlet.pull_chunk()
    if samples is not None and len(samples) > 0:
        time_series_buffer.extend(samples)

def update_evaluation():
    global last_evaluation_time, time_series_buffer, tsfel_configuration, model, prediction, frequency
    if len(time_series_buffer) < tsml.SAMPLING_FREQUENCY * 1000 / frequency / 2:
        return
    elif time.time() - last_evaluation_time < frequency / 1000:
        return
    else:
        last_evaluation_time = time.time()
        df = pandas.DataFrame(data = {
            tsml.CHANNELS[i]: [sample[i+1] for sample in time_series_buffer]
            for i in range(len(tsml.CHANNELS))
        })
        features = tsfel.time_series_features_extractor(
            config=tsfel_configuration, 
            timeseries=df,
            fs=tsml.SAMPLING_FREQUENCY,
            verbose=0,
        )
        
        prediction = model.predict(features)
        time_series_buffer.clear()
        print("Updated Prediction", prediction)

def on_key(e: keyboard.KeyboardEvent):
    global exited
    if e.name == "esc":
        exited = True

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Run the live evalution with the following parameters:")
    parser.add_argument("-i", "--input-filename", default="temp", type=str, help="The input filename of the trained model.")
    parser.add_argument("-f", "--frequency", default=1000, type=int, help="The evaluation interval. (in ms)")
    parser.add_argument("-d", "--domain", default="all", type=str, choices=tsml.TSFEL_FEATURE_DOMAINS, help="The tsfel domain to be used. (all if omitted)")
    args = parser.parse_args()

    start_end_logger = TimeLogger(f"live_evaluation.py\tStart\t{args}", "live_evaluation.py\tDone\t{duration:0.2f}")
    start_end_logger.start()

    # Parameters
    input_filename = args.input_filename
    frequency = args.frequency
    domain = args.domain

    tsfel_configuration = tsfel.get_features_by_domain(domain != "all" and domain or None)

    with TimeLogger("Loading Model", "Done\t{duration:.2f}", separator="\t"):
        with open(train_model.get_filename(input_filename), 'rb') as file:
            model = pickle.load(file)

    with TimeLogger("Setup OpenSignals Stream"	, "Done\t{duration:.2f}", separator="\t"):
        time_series_stream_info = next((stream_info for stream_info in pylsl.resolve_streams() if stream_info.name() == "OpenSignals"), None)
        time_series_inlet = time_series_stream_info is not None and pylsl.StreamInlet(time_series_stream_info) or None
        time_series_buffer: list[list[float]] = []
    if time_series_stream_info is None:
        print("Not found")
        exit()

    # Main Loop
    prediction = 0
    last_evaluation_time = 0
    exited = False
    keyboard.hook(on_key)
    while not exited:
        fetch_time_series()
        update_evaluation()
        time.sleep(0)

    start_end_logger.end()