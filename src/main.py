import subprocess, multiprocessing
import os
import tkinter.simpledialog

participant = tkinter.simpledialog.askstring(title="Participant", prompt="Enter the participant identifier:\t\t") or 'test'
window_size = 100
window_overlap = 0
feature_domain = "all" # all, temporal, statistical, spectral, fractal
model = "RandomForestClassifier"
trained_model_filename = f"model_{participant}"
live_evaluation_frequency = 100

#subprocess.run(["python", os.path.join("src", "recording_app.py"), "-pa", participant])
subprocess.run(["python", os.path.join("src", "extract_features.py"), "-ws", str(window_size), "-wo", str(window_overlap), "-pa", participant, "-d", feature_domain])
subprocess.run(["python", os.path.join("src", "train_model.py"), "-ws", str(window_size), "-wo", str(window_overlap), "-o", trained_model_filename, "-pa", participant])
subprocess.run(["python", os.path.join("src", "live_evaluation.py"), "-ws", str(window_size), "-f", str(live_evaluation_frequency), "-i", trained_model_filename, "-d", feature_domain])