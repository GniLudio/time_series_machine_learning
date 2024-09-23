import os
import typing
import cv2.typing
import tsfel

# PARAMETER
SAMPLING_FREQUENCY = 2000

# RECORDING APP
RECORDING_APP_NUMBER_OF_EXPRESSIONS = 9
RECORDING_APP_EXPRESSION_DURATION = 5
RECORDING_APP_WEBCAM_RESOLUTION_WIDTH = 1920 # to bypass opencv default webcam resolution of (640, 480)
RECORDING_APP_WEBCAM_RESOLUTION_HEIGHT = 1080 # to bypass opencv default webcam resolution of (640, 480)
RECORDING_APP_MAX_SESSION_NUMBER = 100_000
RECORDING_APP_THEME = "clam"
RECORDING_APP_SURVEY_THEME = "xpnative"
RECORDING_APP_CONTINUE_MESSAGE = "Do you want to continue?"
RECORDING_APP_FEEDBACK_QUESTION = "How satisfied were you with the expression?"
RECORDING_APP_FEEDBACK_ANSWERS = ["Not at all", "Very"]
RECORDING_APP_PREVIEW_INSTRUCTION = lambda window: ([
    "Keep your expression neutral and relaxed.", #AU0
    "Raise the inner corners of your eyebrows strongly.", # AU1
    "Raise the inner corners of your eyebrows slightly.", # AU1
    "Raise the outer corners of your eyebrows strongly.", # AU2
    "Raise the outer corners of your eyebrows slightly.", # AU2
    "Lower your eyebrows and draw them together strongly.", # AU4
    "Lower your eyebrows and draw them together slightly.", # AU4
    "Wrinkle your nose, letting your lips part strongly.", # AU9
    "Wrinkle your nose, letting your lips part slightly.", # AU9
    "Let the corners of your lips come up strongly.", # AU12
    "Let the corners of your lips come up slightly.", # AU12
    "Push your lower lip up, thereby raising your chin strongly.", # AU17
    "Push your lower lip up, thereby raising your chin slightly.", # AU17
    "Stretch your mouth horizontally, pulling your lip corners back toward your ears strongly.", # AU20
    "Stretch your mouth horizontally, pulling your lip corners back toward your ears slightly.", # AU20
    "Press your lips together strongly.", # AU24
    "Press your lips together slightly.", # AU24
])[window.getvar("label")]
RECORDING_APP_WEBCAM_INSTRUCTION = lambda window: f"An instruction for the webcam can be placed here."
RECORDING_APP_TITLE = lambda window: f"TSML - Participant {window.getvar("participant")} - Session {window.getvar("session")} - Trial {window.getvar("trial")} - Action Unit {window.getvar("label")}"
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
RECORDING_APP_INSTRUCTIONS = """
Please press Ok after you have read the Instructions
1. Once you click on OK, you will be shown a prompt to enter the filename as instructed to you beforehand.
2. After entering the filename, the experiment window will be displayed. The experiment window contains four sections: (i) Stimulus (ii)Webcam Feed (iii)Controls (iv) Feedback
3. You are expected to practice mimicking the expression shown in the stimulus video  using the webcam feed as a reference.
4. Each expression should be performed twice:
First, at peak intensity (e.g., a broad smile).
Second, in a subtle manner, with minimal muscle movement (e.g., a subtle smile).
5. Once you are confident with your expression, press 'Record'.
6. Your webcam feed should display a red text "recording". Hold the expression until the text dissapears.
7. Please submit feedback in the bottom right window  about how your confident you feel in your expression matching the stimulus video.
8. Click 'Next' to move on to the next stimulus video.
9. All stimulus videos will be shown in sequential order followed by their recording
"""

# Types
type TsfelFeatureDomain = typing.Literal["all", "statistical", "temporal", "spectral", "fractal"]
TSFEL_FEATURE_DOMAINS: tuple[str] =     ["all"] + [tsfel.get_features_by_domain().keys()]
TSFEL_FEATURES = [feature for domain in tsfel.get_features_by_domain().values() for feature in domain.keys()]
# Columns
type Channel = typing.Literal["Channel 1", "Channel 2"]
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