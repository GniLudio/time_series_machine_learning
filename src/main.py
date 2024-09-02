import subprocess
import os
import utils
import itertools
import tsml

window_sizes = [100]
window_overlaps = [0] 
models = ["RandomForestClassifier"]

# Extracting Features
#with utils.TimeLogger("Extracting Features", "Extracting Features\tDone\t{duration:.2f}"):
#    for window_size in window_sizes:
#        for window_overlap in window_overlaps:
#            subprocess.run(["python", os.path.join("src", "extract_features.py"), "-ws", str(window_size), "-wo", str(window_overlap)])

# Cross Validation

with utils.TimeLogger("Cross Validating", "Cross Validating\tDone\t{duration:.2f}"):
    feature_combinations: list[tuple[str, str, str]] = itertools.combinations(tsml.TSFEL_FEATURES, 3)
    feature_combinations: list[str] = [" ".join([f"-f '{feature}'" for feature in set(combination)]) for combination in feature_combinations if len(set(combination)) == len(combination)]
    for window_size in window_sizes:
        for window_overlap in window_overlaps:
            for model in models:
                for feature_combination in feature_combinations:
                    subprocess.run(["python", os.path.join("src", "cross_validation.py"), "-pd", "-ws", str(window_size), "-wo", str(window_overlap), "-m", model, feature_combination])