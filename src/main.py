import subprocess, multiprocessing
import os
import tkinter.simpledialog

participant = "yvo" # tkinter.simpledialog.askstring(title="Participant", prompt="Enter the participant identifier:\t\t") or 'test'
window_sizes = [100, 250, 500, 1000, 2500, 5000]
window_overlap = 0
feature_domains = ["all", "temporal", "statistical", "fractal"] # all, temporal, statistical, spectral, fractal
models = ["GaussianNB", "LinearSVC", "MLPClassifier", "RandomForestClassifier", "SVC"]
trained_model_filename = f"model_{participant}"


#subprocess.run(["python", os.path.join("src", "recording_app.py"), "-pa", participant])
#subprocess.run(["python", os.path.join("src", "train_model.py"), "-ws", str(window_size), "-wo", str(window_overlap), "-o", trained_model_filename, "-pa", participant])
#subprocess.run(["python", os.path.join("src", "live_evaluation.py"), "-ws", str(window_size), "-f", str(live_evaluation_frequency), "-i", trained_model_filename, "-d", feature_domain])

for a, window_size in enumerate(window_sizes):
    for b, feature_domain in enumerate(feature_domains):
        print(f"{str(a).rjust(5)} / {str(len(window_sizes)).ljust(5)}", f"{str(b).rjust(5)} / {str(len(feature_domains)).ljust(5)}")
        subprocess.run(["python", os.path.join("src", "extract_features.py"), "-ws", str(window_size), "-wo", str(window_overlap), "-pa", participant, "-d", feature_domain])
        for c, model in enumerate(models):
            print(f"{str(a).rjust(5)} / {str(len(window_sizes)).ljust(5)}", f"{str(b).rjust(5)} / {str(len(feature_domains)).rjust(5)}", f"{str(c).rjust(5)} / {str(len(models)).ljust(5)}")
            subprocess.run(["python", os.path.join("src", "cross_validation.py"), "-ws", str(window_size), "-wo", str(window_overlap), "-pa", participant, "-d", feature_domain, "-m", model], stdout=subprocess.DEVNULL)