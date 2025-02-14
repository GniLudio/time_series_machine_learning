# Time Series Machine Learning

## Scripts

### Settings

> `src/tsml.py`

-   A configuration file with shared settings, types and more.

### Utils

> `src/utils.py`

-   Some utility functions. (time logging and file naming)

### Recording App

> `src/recording_app.py` -> `data/recordings/`

1. Parse arguments
    - Can be used to set participant name.
2. Set up the GUI
    - see [Sketch](./resources/recording_app_sketch.png)
3. Load videos and webcam
4. Set up variables to store the recordings
    - Create buffers
    - Open OpenSignals stream
5. Set up identifiers
    - Ask for participant name (if not passed as argument)
    - Figure out session number
        - looks for previous sessions in `data/recordings/`
6. Save data after each action unit
    - When the participant presses the `Next/Submit` button
    * When the participant repeats the action unit, only the last one is saved

### Extract Features

> `data/recordings/time_series/` -> `src/extract_features.py` -> `data/features/*.csv`

1. Parse arguments
2. Get output filename
3. Load data
    - time series recordings
4. Group data based on additional data
    - So each action unit is one group
5. Create tsfel configuration
6. Extract features
    - using `tsfel`
7. Add additional data to feature dataframe
8. Write data to output file
9. Continue with step 6. for each action unit

### Cross Validation

> `data/features/*.csv` -> `src/cross_validation.py` -> `data/cross_validation/cv*.csv`

1. Parse arguments
2. Get input and output filenames
3. Load data (features)
    - Splits data into actual and additional data
    - Drops data based on arguments (e.g. channels, familiarity)
4. If person-dependent
    - Splits/Groups/Separates data per participant
5. Create model
6. Create dataframe for results
    - Adds additional data
7. Run the cross validation
    - Using `cross_val_predict` from sklearn
    - Ensures that windows from the same sample are in the same fold. (through the `groups` parameter)
8. Add the predictions to the result dataframe
9. Write the result dataframe to the output file
10. If person-dependent
    - Continue with step 5. for each participant

#### Models

> `src/models.py`

A list of classifiers used by the cross validation.

-   uses `sklearn` models

### Generate Images

* `data/cross_validations/` -> `src/generate_images.py` -> `data/images/`
    * generates bar plots: participant comparison, action unit comparison
    * confusion matrix: for each participant, for all participants

* `data/cross_validations/` -> `src/generate_comparisons.py` -> `data/images/`
    * generates barplots for specific comparisons
    * (easy to add more)

## Images

### General
* some images and videos for the GUI evolutions

### Old images

* without raw predictions 
    * images can't be edited 
* often without detailed annotations
* hard to check in retrospect
    * if I remember right, limiting the sessions and trials were bugged 
* only person-dependent

* Person Dependent Cross Validation with varying parameters:
    * Model: KNN, Random Forest, Gaussian Naive Bayes, Support Vector Machine
    * Feature Domain: all, temporal
    * Participant Count: 1, 3, 5, 10, 31 (all)
    * Session Count: 5, 10, all
    * Trial Count: 5, 10, all
    * Channels: all, frontalis, zygomaticus, corrugator, levator
    * Grouping: With and without 

### Raw Predictions
> `model_results/cross_validation/` and `model_results/raw/`

* Person-Independent:
    * Models: Random Forest, AdaBoost, Bagging, CalibratedClassifierCV, DecisionTree, GaussianNB, GradientBoosting, KNN, LinearSVC, MLP, SVC
* Person-Dependent:
    * Models: KNN, RF, GNB, SVM
    * Window Sizes: 100, 200, 400, 800, 1000
    * Window Overlaps: 0, 20, 25, 50
    * Folds: Stratified 5 Fold, By participant, by session, by trial
    * Channels: All and each alone
    * Minimum Rating: all, >=1, >=2, >=3, >=4, =5
    * Good/Bad participants: all, only best 50%
    * Limit Action Units: All, Only first 5

### Comparisons
* Window Size
* Models
    * Person-Dependent
    * Person-Indpendent
* Channels
* Non Grouped (9 AUs) vs Grouped (1/2/4 and 17/20/24)
* Fold Strategies (statefied, participant, session, trial, action unit)
* Minimum Ratings
    

