import os
import typing
import cv2.typing
import tsfel

# PARAMETER
SAMPLING_FREQUENCY = 2000

# RECORDING APP
RECORDING_APP_NUMBER_OF_EXPRESSIONS = 1
RECORDING_APP_EXPRESSION_DURATION = 1
RECORDING_APP_WEBCAM_RESOLUTION_WIDTH = 1920 # to bypass opencv default webcam resolution of (640, 480)
RECORDING_APP_WEBCAM_RESOLUTION_HEIGHT = 1080 # to bypass opencv default webcam resolution of (640, 480)
RECORDING_APP_MAX_SESSION_NUMBER = 100_000
RECORDING_APP_THEME = "clam"
RECORDING_APP_SURVEY_THEME = "xpnative"
RECORDING_APP_CONTINUE_MESSAGE = "Do you want to continue?"
RECORDING_APP_FEEDBACK_QUESTION = "How satisfied were you with the expression?"
RECORDING_APP_FEEDBACK_ANSWERS = ["Not at all", "Very"]
RECORDING_APP_PREVIEW_INSTRUCTION = lambda window: ([
    "An instruction for the preview can be placed here.",
    "An instruction for the second expression can be placed here.",
    "This should be self-explanatory now.",
    "I hope you don't have an further questions.",
])[window.getvar("label")]
RECORDING_APP_WEBCAM_INSTRUCTION = lambda window: f"An instruction for the webcam can be placed here."
RECORDING_APP_TITLE = lambda window: f"TSML - Participant {window.getvar("participant")} - Session {window.getvar("session")} - Trial {window.getvar("trial")} - Label {window.getvar("label")}"
RECORDING_APP_SURVEY_TITLE = "Survey"
RECORDING_APP_SURVEY_QUESTIONS =  [
    { "type": "Text", "text": "Some Text"},
    { "type":"Checkbutton", "label": "Question 1", "initial": False},
    { "type":"Radiobutton", "label": "Question 2", "initial": "Initial Radio", "values": ["Initial Radio", "Other Radio", "Another Radio"]},
    { "type":"TextInput", "label": "Question 3", "initial": "Initial Text"},
    { "type":"Dropdown", "label": "Question 4", "initial": "Initial Dropdown", "values": ["Initial Dropdown", "Other Dropdown", "Another Dropdown"]},
    { "type":"Slider1", "label": "Question 5", "initial": 3.0, "min": 1.0, "max": 5.0},
    { "type":"Slider2", "label": "Question 5", "initial": 50.0, "min": 1.0, "max": 100.0},
    { "type": "Spinbox", "label": "Question 6", "initial": 33, "min": 3, "max": 333, "step": 11},
]

# Types
type TsfelFeatureDomain = typing.Literal["all", "statistical", "temporal", "spectral", "fractal"]
TSFEL_FEATURE_DOMAINS: tuple[str] =     ["all"] + [tsfel.get_features_by_domain().keys()]
TSFEL_FEATURES = [feature for domain in tsfel.get_features_by_domain().values() for feature in domain.keys()]
# Columns
type Channel = typing.Literal["Corrugator_Supercili", "Frontalis", "Levator_Labii_Superioris", "Zygomaticus_Major"]
CHANNELS: tuple[str] =       ["Corrugator_Supercili", "Frontalis", "Levator_Labii_Superioris", "Zygomaticus_Major"]

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