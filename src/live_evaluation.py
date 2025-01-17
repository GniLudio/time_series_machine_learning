import argparse
import tsfel
import pickle
import pylsl
import keyboard
import time
import pandas

import sys
sys.path.append('.')
from modules.facsvatar.modules.facsvatarzeromq import FACSvatarZeroMQ

import tsml
import train_model
from utils import TimeLogger

def fetch_time_series():
    global time_series_inlet, time_series_timings, time_series_buffer

    (samples, timings) = time_series_inlet.pull_chunk()
    time_series_timings.extend(timings)
    time_series_buffer.extend(samples)

def update_evaluation():
    global time_series_buffer, tsfel_configuration, model, prediction, last_evaluation_time
    window_start = time.time() - window_size
    window_start_index = next((i for i in range(len(time_series_timings)) if time_series_timings[i] > window_start), len(window_start_index))
    time_series_buffer = time_series_buffer[window_start_index:]
    time_series_timings = time_series_timings[window_start_index:]

    if len(time_series_buffer) < 62: # minimum required samples for tsfel
        return False
    else:
        last_evaluation_time = time.time()
        df = pandas.DataFrame(data=[sample[1:] for sample in time_series_buffer], columns=tsml.CHANNELS)
        features = tsfel.time_series_features_extractor(
            config=tsfel_configuration, 
            timeseries=df,
            fs=tsml.SAMPLING_FREQUENCY,
            verbose=0,
        )
        prediction = model.predict(features)[0]
        return True

class FACSvatarMessages(FACSvatarZeroMQ):
    """Receives FACS and Head movement data; forward to output function"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.exited = False

    async def sub(self):
        global prediction

        AU_TO_NAME = {
            **{au: f"AU0{au}" for au in range(0, 10)},
            **{au: f"AU{au}" for au in range(10, 25)},
        }

        # Main Loop
        exited = False
        keyboard.hook(lambda e: self.on_key(e))
        while not self.exited:
            fetch_time_series()
            if time.time() - last_evaluation_time < frequency / 1000:
                update_evaluation()
                last_evaluation_time = time.time()
                
                print(prediction)
                au_data = {"AU01": 0.0,"AU02": 0.0,"AU04": 0.0,"AU05": 0.0,"AU06": 0.0,"AU07": 0.0,"AU09": 0.0,"AU10": 0.0,"AU12": 0.0,"AU14": 0.0,"AU15": 0.0,"AU17": 0.0,"AU20": 0.0,"AU23": 0.0,"AU25": 0.0,"AU26": 0.0,"AU45": 0}
                au_data[tsml.INDEX_TO_AU[prediction]] = 1.0
                await self.pub_socket.pub({
                    "confidence": 1, 
                    "frame": -1, 
                    "timestamp": time.time(), 
                    "au_r": au_data,
                    "gaze": {"gaze_angle_x": 0,"gaze_angle_y": 0},
                    "pose": {"pose_Rx": 0,"pose_Ry": 0,"pose_Rz": 0},
                    "timestamp_utc": 0
                })
            time.sleep(0.01)

        return

    def on_key(self, event: keyboard.KeyboardEvent):
        if event.name == "esc":
            print("Pressed", "Escape")
            self.exited = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Run the live evalution with the following parameters:")
    # Model Parameters
    parser.add_argument("-i", "--input-filename", type=str, help="The filename of the trained model.")
    parser.add_argument("-f", "--frequency", default=1000, type=int, help="The evaluation frequency. (in ms)")
    parser.add_argument("-d", "--domain", default="all", choices=tsml.TSFEL_FEATURE_DOMAINS, help="The tsfel domain to be used. (all if omitted)")
    parser.add_argument("-ws", "--window-size", default=1000, type=int, help="The window size. (in ms)")
    # Facsvatar Parameter
    parser.add_argument("--pub_ip", default=argparse.SUPPRESS, help="IP (e.g. 192.168.x.x) of where to pub to; Default: 127.0.0.1 (local)")
    parser.add_argument("--pub_port", default="5570", help="Port of where to pub to; Default: 5570")
    parser.add_argument("--pub_key", default="gui.face_config", help="Key for filtering message; Default: openface")
    parser.add_argument("--pub_bind", default=False, help="True: socket.bind() / False: socket.connect(); Default: False")

    args, leftovers = parser.parse_known_args()

    start_end_logger = TimeLogger(f"live_evaluation.py\tStart\t{args}", "live_evaluation.py\tDone\t{duration:0.2f}")
    start_end_logger.start()

    # Model Parameters
    input_filename = args.input_filename
    frequency = args.frequency
    domain = args.domain
    window_size = args.window_size
    del args.input_filename
    del args.frequency
    del args.domain
    del args.window_size
    
    last_evaluation_time = 0
    prediction = 0

    tsfel_configuration = tsfel.get_features_by_domain(domain != "all" and domain or None)

    with TimeLogger("Load Model", "Done\t{duration:.2f}", separator="\t"):
        with open(train_model.get_filename(input_filename), 'rb') as file:
            model = pickle.load(file)

    with TimeLogger("Setup OpenSignals Stream"	, "Done\t{duration:.2f}", separator="\t"):
        time_series_stream_info = next((stream_info for stream_info in pylsl.resolve_streams() if stream_info.name() == "OpenSignals"), None)
        time_series_inlet = time_series_stream_info is not None and pylsl.StreamInlet(time_series_stream_info) or None
        time_series_timings: list[float] = []
        time_series_buffer: list[list[float]] = []

    with TimeLogger("Setup Facsvatar", "Done\t{duration:.2f}"):
        facsvatar_messages = FACSvatarMessages(**vars(args))
        facsvatar_messages.start([facsvatar_messages.sub])
    
    start_end_logger.end()