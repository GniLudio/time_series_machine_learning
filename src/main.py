import subprocess
import os
import utils

window_sizes = [100, 200, 250, 500, 1000, 2000, 4000]
window_overlaps = [0, 1, 2, 3, 4, 5, 10, 25, 50] 
models = ["RandomForestClassifier", "GaussianNB", "KNeighborsClassifier", "LinearSVC", "MLPClassifier", "RandomForestClassifier", "SVC"]

# Extracting Features
with utils.TimeLogger("Extracting Features", "Extracting Features\tDone\t{duration:.2f}"):
    for window_size in window_sizes:
        for window_overlap in window_overlaps:
            with utils.TimeLogger(f"\t{window_size} - {window_overlap}", "Done\t{duration:.2f}", separator="\t"):
                subprocess.run(["python", os.path.join("src", "extract_features.py"), "-ws", str(window_size), "-wo", str(window_overlap)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Cross Validation
with utils.TimeLogger("Cross Validating", "Cross Validating\tDone\t{duration:.2f}"):
    for window_size in window_sizes:
        for window_overlap in window_overlaps:
            for model in models:
                with utils.TimeLogger(f"\t{window_size} - {window_overlap} - {model}", "Done\t""{duration:.2f}", separator="\t"):
                    subprocess.run(["python", os.path.join("src", "cross_validation.py"), "-dp", "-ws", str(window_size), "-wo", str(window_overlap)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)