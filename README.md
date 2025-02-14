# Nodes

## Settings

> `src/tsml.py`

-   A configuration file with shared settings, types and more.

## Utils

> `src/utils.py`

-   Some utility functions. (time logging and file naming)

## Recording App

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
6. Save data after each trial/sample
    - When the participant presses the `Next/Submit` button
    * When the participant repeated the trial only the last one is saved

## Extract Features

> `data/recordings/time_series/` -> `src/extract_features.py` -> `data/features/*.csv`

1. Parse arguments
2. Get output filename
3. Load data
    - time series recordings
4. Group data based on additional data
    - So each sample/trial (e.g. action unit) is one group
5. Create tsfel configuration
6. Extract features
    - using `tsfel`
7. Add additional data to feature dataframe
8. Write data to output file
9. Continue with step 6. for each sample/trial

## Cross Validation

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

### Models

> `src/models.py`

A list of classifiers used by the cross validation.

-   uses `sklearn` models

## Generate Images

> `data/cross_validations/` -> `src/generate_images.py` -> `data/images/`
