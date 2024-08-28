import os
import typing
import cv2.typing

# PARAMETER
SAMPLING_FREQUENCY = 2000
NUMBER_OF_EXPRESSIONS = 4

# RECORDING APP
RECORDING_APP_EXPRESSION_DURATION = 10
RECORDING_APP_WEBCAM_RESOLUTION_WIDTH = 1920 # to bypass opencv default webcam resolution of (640, 480)
RECORDING_APP_WEBCAM_RESOLUTION_HEIGHT = 1080 # to bypass opencv default webcam resolution of (640, 480)
RECORDING_APP_MAX_SESSION_NUMBER = 100_000
RECORDING_APP_PREVIEW_INSTRUCTION = lambda window: ([
    "An instruction for the preview can be placed here.",
    "An instruction for the second expression can be placed here.",
    "This should be self-explanatory now.",
    "I hope you don't have an further questions.",
])[window.getvar("label")]

RECORDING_APP_WEBCAM_INSTRUCTION = lambda window: f"An instruction for the webcam can be placed here."

# Types
type TsfelFeatureDomain = typing.Literal["all", "statistical", "temporal", "spectral", "fractal"]
TSFEL_FEATURE_DOMAINS: tuple[str] =     ["all", "statistical", "temporal", "spectral", "fractal"]

# Columns
type Channel = typing.Literal["Ch1", "Ch2"]
CHANNELS: tuple[str] =       ["Ch1", "Ch2"]

type AdditionalColumn = typing.Literal["Participant", "Session", "Trial", "Action Unit", "Feedback"]
ADDITIONAL_COLUMNS: tuple[str] =      ["Participant", "Session", "Trial", "Action Unit", "Feedback"]
LABEL_COLUMN = "Action Unit"
PARTICIPANT_COLUMN = "Participant"

type WebcamBuffer = list[cv2.typing.MatLike]
type TimeSeriesBuffer = list[list[float]]

# Pandas
DATASET_DTYPE = {
    **{channel: 'float64' for channel in CHANNELS},
    'Participant': 'object',
    'Session': 'int64',
    'Trial': 'int64',
    'Action Unit': 'int64',
    'Feedback': 'int64',
}

# Paths
## Recordings
DATA_DIRECTORY = 'data'
RECORDING_DIRECTORY = os.path.join(DATA_DIRECTORY, 'recordings')
RECORDING_TIMESERIES_DIRECTORY = os.path.join(RECORDING_DIRECTORY, 'time_series')
RECORDING_WEBCAM_DIRECTORY = os.path.join(RECORDING_DIRECTORY, 'webcam')
RECORDING_FEEDBACK_DIRECTORY = os.path.join(RECORDING_DIRECTORY, 'feedback')
RECORDING_SURVEY_DIRECTORY = os.path.join(RECORDING_DIRECTORY, 'survey')
## Resources
RESOURCES_DIRECTORY = 'resources'
RESOURCES_PREVIEWS_DIRECTORY = os.path.join(RESOURCES_DIRECTORY, 'previews')

FEATURES_DIRECTORY = os.path.join(DATA_DIRECTORY, 'features')
CROSS_VALIDATION_DIRECTORY = os.path.join(DATA_DIRECTORY, 'cross_validation')
CROSS_VALIDATION_PERSON_DEPENDENT_DIRECTORY = os.path.join(CROSS_VALIDATION_DIRECTORY, 'person_dependent')
CROSS_VALIDATION_PERSON_INDEPENDENT_DIRECTORY = os.path.join(CROSS_VALIDATION_DIRECTORY, 'person_independent')