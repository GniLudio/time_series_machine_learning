import os
import typing
import cv2.typing
import tsfel

# PARAMETER
SAMPLING_FREQUENCY = 2000

# RECORDING APP
RECORDING_APP_NUMBER_OF_EXPRESSIONS = 9
RECORDING_APP_EXPRESSION_DURATION = 5
RECORDING_APP_TRIAL_COUNT = 1
RECORDING_APP_WEBCAM_RESOLUTION_WIDTH = 1920 # to bypass opencv default webcam resolution of (640, 480)
RECORDING_APP_WEBCAM_RESOLUTION_HEIGHT = 1080 # to bypass opencv default webcam resolution of (640, 480)
RECORDING_APP_PREVIEW_PLAYBACK_SPEED = 0.5
RECORDING_APP_MAX_SESSION_NUMBER = 100_000
RECORDING_APP_THEME = "clam"
RECORDING_APP_SURVEY_THEME = "xpnative"
RECORDING_APP_CONTINUE_MESSAGE = "Do you want to continue?"
RECORDING_APP_FEEDBACK_QUESTION = "How satisfied were you with the expression?"
RECORDING_APP_FEEDBACK_ANSWERS = ["Not at all", "Very"]
RECORDING_APP_PREVIEW_INSTRUCTION = lambda window: ([
    "Keep your expression neutral and relaxed.", #AU0
    "Raise the inner corners of your eyebrows.", # AU1
    "Raise the outer corners of your eyebrows.", # AU2
    "Lower your eyebrows and draw them together.", # AU4
    "Wrinkle your nose, letting your lips part.", # AU9
    "Let the corners of your lips come up.", # AU12
    "Push your lower lip up, thereby raising your chin .", # AU17
    "Stretch your mouth horizontally, pulling your lip corners back toward your ears.", # AU20
    "Press your lips together.", # AU24
])[window.getvar("label")]
RECORDING_APP_WEBCAM_INSTRUCTION = lambda window: f"Start and then hold the expression for {RECORDING_APP_EXPRESSION_DURATION}s after pressing the START button."
RECORDING_APP_TITEL_LABEL_NAMES = [
    " 0 (Neutral)",
    " 1",
    " 2",
    " 4",
    " 9",
    "12",
    "17",
    "20",
    "24",
]
INDEX_TO_AU = [
    "AU00",
    "AU01",
    "AU02",
    "AU04",
    "AU09",
    "AU12",
    "AU17",
    "AU20",
    "AU24",
]
RECORDING_APP_TITLE = lambda window: (
    "TSML" 
    + f" - Participant {window.getvar("participant")}" 
    + f" - Session {window.getvar("session")}"
    + f" - Trial {window.getvar("trial")}"
    + f" - Action Unit {RECORDING_APP_TITEL_LABEL_NAMES[window.getvar("label")]}"
    + f" - {window.getvar("label")}"
)
RECORDING_APP_SURVEY_TITLE = "Survey"
RECORDING_APP_SURVEY_QUESTIONS =  [
    #{ "type":"Slider1", "label": "How much did you feel the presence of the electrodes on the upper face?", "initial": 1.0, "min": 1.0, "max": 5.0},
    #{ "type":"Slider1", "label": "How much did you feel the presence of the electrodes on the lower face?", "initial": 1.0, "min": 1.0, "max": 5.0},
    #{ "type":"Slider1", "label": "Compared to having no electrodes, how difficult did it feel to move the muscles on the upper face?", "initial": 1.0, "min": 1.0, "max": 5.0},
    #{ "type":"Slider1", "label": "Compared to having no electrodes, how difficult did it feel to move the muscles on the lower face?", "initial": 1.0, "min": 1.0, "max": 5.0}
]
'''
    { "type": "Text", "text": "Some Text"},
    { "type":"Checkbutton", "label": "Question 1", "initial": False},
    { "type":"Radiobutton", "label": "Question 2", "initial": "Initial Radio", "values": ["Initial Radio", "Other Radio", "Another Radio"]},
    { "type":"TextInput", "label": "Question 3", "initial": "Initial Text"},
    { "type":"Dropdown", "label": "Question 4", "initial": "Initial Dropdown", "values": ["Initial Dropdown", "Other Dropdown", "Another Dropdown"]},
    { "type":"Slider1", "label": "Question 5", "initial": 3.0, "min": 1.0, "max": 5.0},
    { "type":"Slider2", "label": "Question 5", "initial": 50.0, "min": 1.0, "max": 100.0},
    { "type": "Spinbox", "label": "Question 6", "initial": 33, "min": 3, "max": 333, "step": 11}
'''

RECORDING_APP_INSTRUCTIONS = f"""
In the following study you will perform multiple action units.

There are a total of {RECORDING_APP_NUMBER_OF_EXPRESSIONS-1} action units (+1 neutral):

For each action unit:
1. Read the description.
2. Practise as long as you like.
3. Press the 'START' button when you are ready.
4. Hold the expression during the recording phase. (~{RECORDING_APP_EXPRESSION_DURATION}s)
    * Indicated by the red border around the webcam.
5. Evaluate how well you performed the expression.
6. Press 'NEXT' to continue with the next action unit.
"""

# Types
type TsfelFeatureDomain = typing.Literal["all", "statistical", "temporal", "spectral", "fractal"]
TSFEL_FEATURE_DOMAINS: tuple[str] =     ["all"] + [tsfel.get_features_by_domain().keys()]
TSFEL_FEATURES = [feature for domain in tsfel.get_features_by_domain().values() for feature in domain.keys()]
# Columns
type Channel = typing.Literal['Lateral Frontalis', 'Corrugator Supercili','Zygomaticus Major','Levator Labii Superioris']
CHANNELS: tuple[str] =       ['Lateral Frontalis', 'Corrugator Supercili','Zygomaticus Major','Levator Labii Superioris']

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

TRAINED_MODEL_DIRECTORY = os.path.join(DATA_DIRECTORY, 'models')