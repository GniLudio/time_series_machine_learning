import tkinter, tkinter.dialog, tkinter.simpledialog, tkinter.messagebox, tkinter.font, tkinter.ttk 
import threading
import multiprocessing, multiprocessing.connection
import threading
import PIL, PIL.Image, PIL.ImageTk
import pylsl
import cv2
import os
import time
import math
import pandas
from utils import TimeLogger, ask_selection, join_filename_parts

import tsml

# STYLE
INSTRUCTION_FONT = ("Helvetica", 12)
INSTRUCTION_FONT_HIGHLIGHT = ("Helvetica", 12, "bold")
BUTTON_FONT = ("Helvetica", 12, "bold")
FEEDBACK_QUESTION_FONT = ("Helvetica", 12, "bold")
FEEDBACK_ANSWER_FONT = ("Arial", 10)
SURVEY_HEADER_FONT = ("Arial", 16, "bold")
SURVEY_LABEL_FONT = ("Arial", 12)
SURVEY_SUBMIT_FONT = ("Arial", 12, "bold")

# Events
NEXT_LABEL_EVENT = '<<NextLabel>>'
VIDEO_PLAY_EVENT = "<<Play>>"
VIDEO_PAUSE_EVENT = "<<Pause>>"
START_RECORDING_EVENT = "<<StartRecording>>"
STOP_RECORDING_EVENT = "<<StopRecording>>"
FEEDBACK_CHANGED_EVENT = "<<FeedbackChanged>>"
WEBCAM_FIRST_FRAME = "<<WebcamFirstFrame>>"

# MISC
EMG_POSITIONS = ["A", "B"]

# Debugging
SHOW_THEME_SELECTOR = False

# Setup
def setup_ui() -> tkinter.Tk:
    # Window
    window = tkinter.Tk()
    window.minsize(width=720, height=480)
    window.withdraw()
    window.title(string="Placeholder title")
    window.grid_rowconfigure(index=0, weight=1)
    window.grid_columnconfigure(index=0, weight=1)
    window.protocol(name='WM_DELETE_WINDOW', func=on_exit)
    window.bind(sequence=NEXT_LABEL_EVENT, func=lambda _: window.title(tsml.RECORDING_APP_TITLE(window)), add=True)

    # Style
    style = tkinter.ttk.Style(master=window)
    style.theme_use(themename=tsml.RECORDING_APP_THEME )
    style.configure(style='Sash', sashthickness=10)
    style.configure(style='TRadiobutton', focusthickness=0)
    style.configure(style="TButton", font=BUTTON_FONT)

    # Root
    root_container = tkinter.ttk.Panedwindow(master=window, name="root", orient='vertical')
    root_container.grid(row=0, column=0, sticky='nsew')

    ## Videos
    video_container = tkinter.ttk.Panedwindow(master=root_container, name="videos", orient='horizontal')
    root_container.add(child=video_container, weight=1)

    ### Preview
    preview_container = tkinter.ttk.Frame(master=video_container, name="preview")
    preview_container.grid_rowconfigure(index=0, weight=1)
    preview_container.grid_rowconfigure(index=1, weight=0)
    preview_container.grid_columnconfigure(index=0, weight=1)
    video_container.add(child=preview_container, weight=3)

    preview_video = tkinter.Label(master=preview_container, name="video", borderwidth=0)
    preview_video.grid(row=0, column=0, sticky='nsew')

    preview_video_play_pause_button = tkinter.ttk.Button(master=preview_container, name="play_pause_button", text="PLAY", command=toggle_preview)
    preview_video_play_pause_button.grid(row=0, column=0, sticky='s', padx=5, pady=5)
    preview_video.bind(VIDEO_PLAY_EVENT, lambda _: preview_video_play_pause_button.configure(text="PAUSE"), add=True)
    preview_video.bind(VIDEO_PAUSE_EVENT, lambda _: preview_video_play_pause_button.configure(text="PLAY"), add=True)

    preview_instruction = tkinter.Frame(master=preview_container, name="instruction")
    preview_instruction.grid(row=1, column=0, padx=10, pady=10, sticky="n")
    window.bind(NEXT_LABEL_EVENT, func=lambda _: preview_instruction_update(), add=True)
    def preview_instruction_update():
        for child in preview_instruction.winfo_children():
            child.destroy()

        for i, part in enumerate(tsml.RECORDING_APP_PREVIEW_INSTRUCTION(window).split("**")):
            font = (i % 2 == 0) and INSTRUCTION_FONT or INSTRUCTION_FONT_HIGHLIGHT
            label = tkinter.ttk.Label(master=preview_instruction, text=part, font=font)
            label.grid(row=0, column=i, padx=0, pady=0, ipadx=0, ipady=0, sticky="ns")

    ### Seperator
    seperator_container = tkinter.ttk.Frame(master=video_container)
    seperator_container.grid_rowconfigure(index=0, weight=1)
    seperator_container.grid_columnconfigure(index=0, weight=1)
    video_container.add(child=seperator_container, weight=1)

    if SHOW_THEME_SELECTOR:
        style = tkinter.ttk.Style()
        variable = tkinter.StringVar(value=style.theme_use())
        tkinter.ttk.Combobox(seperator_container, values=style.theme_names(), textvariable=variable).grid(sticky="n")
        variable.trace_add("write", lambda _, __, ___: style.theme_use(variable.get() or style.theme_use()))

    ### Webcam
    webcam_container = tkinter.ttk.Frame(master=video_container, name="webcam")
    webcam_container.grid_rowconfigure(index=0, weight=1)
    webcam_container.grid_rowconfigure(index=1, weight=0)
    webcam_container.grid_columnconfigure(index=0, weight=1)
    video_container.add(child=webcam_container, weight=3)

    webcam_video = tkinter.Label(master=webcam_container, name="video")
    webcam_video.grid(row=0, column=0, sticky="nsew")

    webcam_instruction = tkinter.ttk.Label(master=webcam_container, name="instruction", justify="center", font=INSTRUCTION_FONT)
    webcam_instruction.grid(row=1, column=0, padx=10, pady=10)
    window.bind(sequence=NEXT_LABEL_EVENT, func= lambda _: webcam_instruction.configure(text=tsml.RECORDING_APP_WEBCAM_INSTRUCTION(window)), add=True)

    ## Controls
    controls_container = tkinter.ttk.Frame(master=root_container, name="controls")
    controls_container.grid_rowconfigure(index=0, weight=1)
    controls_container.grid_rowconfigure(index=1, weight=0)
    controls_container.grid_rowconfigure(index=2, weight=1)
    controls_container.grid_columnconfigure(index=0, weight=1)
    root_container.add(child=controls_container, weight=0)

    ### Start Recording
    start_recording_button = tkinter.ttk.Button(master=controls_container, name="start_recording", text="LOADING", command=lambda: window.setvar(name="recording_active", value=True))
    start_recording_button.configure(state='disabled')
    start_recording_button.grid(row=0, column=0, sticky="s", padx=10, pady=10)
    window.bind(sequence=WEBCAM_FIRST_FRAME, func=lambda _: start_recording_button.configure(state="active", text="START"), add=True)
    window.bind(sequence=START_RECORDING_EVENT, func=lambda _: start_recording_button.configure(state="disabled", text="RECORDING"), add=True)
    window.bind(sequence=STOP_RECORDING_EVENT, func=lambda _: start_recording_button.configure(state="active", text="RESTART"), add=True)
    window.bind(sequence=WEBCAM_FIRST_FRAME, func=lambda _: window.bind(sequence=NEXT_LABEL_EVENT, func=lambda _: start_recording_button.configure(state="active", text="START"), add=True), add=True)

    ### Feedback
    feedback_container = tkinter.ttk.Frame(master=controls_container, name="feedback")
    feedback_container.grid(row=1, column=0, padx=10, pady=0)

    tkinter.ttk.Label(feedback_container, text=tsml.RECORDING_APP_FEEDBACK_QUESTION, font=FEEDBACK_QUESTION_FONT).grid(row=0, column=0, columnspan=7)
    tkinter.ttk.Label(feedback_container, text=tsml.RECORDING_APP_FEEDBACK_ANSWERS[0], font=FEEDBACK_ANSWER_FONT).grid(row=1, column=0)
    for i in range(5):
        feedback_radiobutton = tkinter.ttk.Radiobutton(master=feedback_container, variable="feedback", value=i+1)
        feedback_radiobutton.grid(row=1, column=i+1)
    set_radiobutton_states = lambda state: [isinstance(widget, tkinter.ttk.Radiobutton) and widget.configure(state=state) for widget in feedback_container.winfo_children()]
    window.bind(sequence=NEXT_LABEL_EVENT, func=lambda e: set_radiobutton_states('disabled'), add=True)
    window.bind(sequence=STOP_RECORDING_EVENT, func=lambda e: set_radiobutton_states('normal'), add=True)
    tkinter.ttk.Label(master=feedback_container, text=tsml.RECORDING_APP_FEEDBACK_ANSWERS[1], font=FEEDBACK_ANSWER_FONT).grid(row=1, column=6)

    ### Next Label
    next_button = tkinter.ttk.Button(controls_container, name="next_label", text="NEXT", command=next_label)
    next_button.grid(row=2, column=0, sticky="n", padx=10, pady=10)
    window.bind(sequence=NEXT_LABEL_EVENT, func=lambda _: next_button.configure(state="disabled"), add=True)
    window.bind(sequence=FEEDBACK_CHANGED_EVENT, func=lambda _: next_button.configure(state=window.getvar("feedback") > 0 and 'active' or 'disabled'), add=True)
    # TODO: Enable next button after feedback is given

    return window

def open_survey():
    global window
    print("Open Survey")

    window.withdraw()

    dialog = tkinter.Toplevel(window)
    dialog.title(tsml.RECORDING_APP_SURVEY_TITLE)
    dialog.protocol("WM_DELETE_WINDOW", on_exit)
    dialog.minsize(width=720, height=480)
    old_theme = tkinter.ttk.Style().theme_use()
    tkinter.ttk.Style().theme_use(tsml.RECORDING_APP_SURVEY_THEME)

    dialog.configure(padx=10, pady=10)
    dialog.grid_rowconfigure(index=0, weight=1)
    dialog.grid_columnconfigure(index=0, weight=1)

    root = tkinter.ttk.Frame(dialog)
    root.grid_rowconfigure(index=0, weight=1)
    root.grid_columnconfigure(index=0, weight=1)
    root.grid(row=0, column=0, sticky="nswe")

    root = tkinter.ttk.LabelFrame(root)
    root.grid(row=0, column=0)

    variables: list[tkinter.Variable] = []
    for i, question in enumerate(tsml.RECORDING_APP_SURVEY_QUESTIONS):
        if question["type"] == "Text":
            label = tkinter.ttk.Label(root, text=question["text"], anchor="center", font=SURVEY_HEADER_FONT)
            label.grid(row=i, column=0, columnspan=2, padx=3, pady=3)
            continue

        label = tkinter.ttk.Label(root, text=question["label"], font=SURVEY_LABEL_FONT)
        widget, variable = None, None
        if question["type"] == "Checkbutton":
            variable = tkinter.BooleanVar(window, value=question["initial"])
            widget = tkinter.ttk.Checkbutton(root, variable=variable)
        elif question["type"] == "Radiobutton":
            variable = tkinter.StringVar(window, value=question["initial"])
            widget = tkinter.ttk.Frame(root)
            for i, option in enumerate(question["values"]):
                radiobutton = tkinter.ttk.Radiobutton(widget, variable=variable, value=option, text=option)
                radiobutton.grid(row=i, column=0, sticky="w")
        elif question["type"] == "TextInput":
            variable = tkinter.StringVar(window, value=question["initial"])
            widget = tkinter.ttk.Entry(root, textvariable=variable)
        elif question["type"] == "Dropdown":
            variable = tkinter.StringVar(window, value=question["initial"])
            widget = tkinter.ttk.Combobox(root, textvariable=variable, values=question["values"])
        elif question["type"] == "Slider1":
            variable = tkinter.StringVar(window, value=question["initial"])
            widget = tkinter.Scale(root, variable=variable, from_=question['min'], to=question['max'], length=200, orient="horizontal")
        elif question["type"] == "Slider2":
            variable = tkinter.StringVar(window, value=question["initial"])
            widget = tkinter.ttk.Scale(root, variable=variable, from_=question['min'], to=question['max'], length=200)
        elif question["type"] == "Spinbox":
            variable = tkinter.StringVar(window, value=question["initial"])
            widget = tkinter.ttk.Spinbox(root, textvariable=variable, from_=question['min'], to=question['max'], increment=question["step"])
        if widget and variable:
            label.grid(row=i, column=0, padx=10, pady=10, sticky="n")
            widget.grid(row=i, column=1, padx=10, pady=10, sticky="w")
            variables.append(variable)

    submit_button = tkinter.Button(root, text="Submit", font=SURVEY_SUBMIT_FONT, command=lambda: on_submit_survey(dialog, variables))
    submit_button.grid(row=len(tsml.RECORDING_APP_SURVEY_QUESTIONS)+1, column=0, columnspan=2, padx=10, pady=10)

    if SHOW_THEME_SELECTOR:
        style = tkinter.ttk.Style()
        variable = tkinter.StringVar(value=style.theme_use())
        tkinter.ttk.Combobox(dialog, values=style.theme_names(), textvariable=variable).grid()
        variable.trace_add("write", lambda _, __, ___: style.theme_use(variable.get()))

    dialog.wait_visibility()
    dialog.geometry(f"+{(dialog.winfo_screenwidth()) // 2}+{dialog.winfo_width() // 2}")
    dialog.grab_set()
    dialog.wait_window()

    tkinter.ttk.Style().theme_use(old_theme)

def setup_videos(window: tkinter.Tk, webcam_path: str, preview_path: str) -> tuple['Webcam', dict[int, 'CV2Video']]:
    webcam_video = window.nametowidget(webcam_path)
    webcam = Webcam(
        container=webcam_video, 
        filename_or_index=0, 
        api_preference=cv2.CAP_ANY,
        flipped=True,
        width=tsml.RECORDING_APP_WEBCAM_RESOLUTION_WIDTH,
        height=tsml.RECORDING_APP_WEBCAM_RESOLUTION_HEIGHT,
        use_fps_delay=False
    )
    window.bind(sequence=START_RECORDING_EVENT, func=lambda _: webcam.set_image_dirty(), add=True)
    window.bind(sequence=STOP_RECORDING_EVENT, func=lambda _: webcam.set_image_dirty(), add=True)

    preview_video = window.nametowidget(preview_path)
    previews = {
        i: CV2Video(
            container=preview_video,
            filename_or_index=os.path.join(tsml.RESOURCES_PREVIEWS_DIRECTORY, f"preview_{i}.mp4"),
            api_preference=cv2.CAP_ANY,
            flipped=False,
            width=None,
            height=None,
            use_fps_delay=True,
            playback_speed=tsml.RECORDING_APP_PREVIEW_PLAYBACK_SPEED,
            use_threading=True,
            looping=True,
        ) for i in range(tsml.RECORDING_APP_NUMBER_OF_EXPRESSIONS)
    }
    for preview in previews.values():
        window.bind(sequence=NEXT_LABEL_EVENT, func=lambda _, p=preview:p.pause(), add=True)

    return webcam, previews

# Actions
def toggle_preview():
    global window, previews
    print("Toggle Preview")
    previews[window.getvar("label")].toggle_play_pause()

def next_label():
    global window, webcam_buffer, time_series_buffer, window_exited

    threading.Thread(
        target=save_recording, 
        daemon=False, 
        args=(
            window.getvar("participant"), 
            window.getvar("session"), 
            window.getvar("emg_positioning"), 
            window.getvar("trial"), 
            window.getvar("label"), 
            time_series_buffer.copy(), 
            webcam_buffer.copy(), 
            window.getvar("feedback")
        )
    ).start()

    if window.getvar("label")+1 < tsml.RECORDING_APP_NUMBER_OF_EXPRESSIONS:
        print("Next Label")
        window.setvar(name="label", value=window.getvar("label")+1)
    else:
        #next_trial = tkinter.messagebox.askyesno(message=tsml.RECORDING_APP_CONTINUE_MESSAGE)
        next_trial = False
        if next_trial:
            print("Next Trial")
            window.setvar(name="trial", value=window.getvar("trial")+1)
            window.setvar(name="label", value=0)
        elif not window.getvar("emg_switched"):
            open_survey()
            tkinter.messagebox.showinfo(title="", message="Switch the electrode positioning.")
            window.state("zoomed")
            window.deiconify()
            window.setvar(name="emg_positioning", value=next(p for p in EMG_POSITIONS if p != window.getvar("emg_positioning")))
            window.setvar(name="trial", value=0)
            window.setvar(name="label", value=0)
            window.setvar(name="emg_switched", value=True)
        else:
            open_survey()
            tkinter.messagebox.showinfo(title="", message="Thanks for participating.")
            window_exited = True

def update_recording():
    global window, time_series_buffer, time_series_inlet

    if time_series_inlet is not None:
        if not window.getvar(name="recording_active"):
            time_series_inlet.flush()
        else:
            (samples, _) = time_series_inlet.pull_chunk()
            if samples is not None and len(samples) > 0 :
                time_series_buffer.extend(samples)

    if window.getvar("recording_active") and time.time() - window.getvar("recording_start") >= tsml.RECORDING_APP_EXPRESSION_DURATION:
        window.setvar(name="recording_active", value=False)
        
def save_recording(participant: str, session: int, emg_positioning: str, trial: int, label: int, time_series_data: tsml.TimeSeriesBuffer, webcam_data: tsml.WebcamBuffer, feedback_data: int):
    base_filename = get_base_output_filename(participant=participant, session=session, emg_positioning=emg_positioning, trial=trial, label=label)
    print("Save Recording", base_filename)

    webcam_filename = get_webcam_output_filename(base_filename)
    os.makedirs(os.path.dirname(webcam_filename), exist_ok=True)
    writer = cv2.VideoWriter(
        filename=webcam_filename, 
        fourcc=cv2.VideoWriter_fourcc(*'MJPG'),
        fps=(len(webcam_data) / tsml.RECORDING_APP_EXPRESSION_DURATION) or 1, 
        frameSize=(webcam.width, webcam.height)
    )
    for frame in webcam_data:
        writer.write(frame)

    time_series_filename = get_time_series_output_filename(base_filename)
    os.makedirs(os.path.dirname(time_series_filename), exist_ok=True)
    time_series_df = pandas.DataFrame(data = {
        tsml.CHANNELS[i]: [sample[i+1] for sample in time_series_data]
        for i in range(len(tsml.CHANNELS))
    })
    time_series_df.to_csv(path_or_buf=time_series_filename,index=False)

    feedback_filename = get_feedback_output_filename(base_filename)
    os.makedirs(os.path.dirname(feedback_filename), exist_ok=True)
    with open(feedback_filename, 'w') as file:
        file.write(str(feedback_data))

def on_exit():
    global window_exited, window
    print("On Exit")
    window_exited = True
    window.destroy()

def on_submit_survey(dialog: tkinter.Toplevel, variables: list[tkinter.Variable]):
    global window
    values = [str(variable.get()) for variable in variables]
    filename = get_survey_output_filename(
        get_base_output_filename(
            participant = window.getvar("participant"), 
            session = window.getvar("session"), 
            emg_positioning= window.getvar("emg_positioning"),
            trial=window.getvar("trial"), 
            label=None
        )
    )
    print("Save Survey", filename, values)

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    pandas.DataFrame(data=values).to_csv(filename, header=False)

    dialog.destroy()

# Paths
def get_base_output_filename(participant: str, session: int, emg_positioning: str, trial: int | None, label: int | None) -> str:
    return join_filename_parts({
        'pa': participant,
        'se': session,
        'po': emg_positioning,
        'tr': trial,
        'la': label,
    })

def get_webcam_output_filename(filename: str) -> str:
    return os.path.join(tsml.RECORDING_WEBCAM_DIRECTORY, filename + ".avi")

def get_time_series_output_filename(filename: str) -> str:
    return os.path.join(tsml.RECORDING_TIMESERIES_DIRECTORY, filename + ".csv")

def get_feedback_output_filename(filename: str) -> str:
    return os.path.join(tsml.RECORDING_FEEDBACK_DIRECTORY, filename + ".txt")

def get_survey_output_filename(filename: str) -> str:
    return os.path.join(tsml.RECORDING_SURVEY_DIRECTORY, filename + ".txt")

def does_session_exist(participant: str, session: int) -> bool:
    return any(os.path.exists(filename) for filename in [
        get_webcam_output_filename(get_base_output_filename(participant, session, EMG_POSITIONS[0], 0, 0)),
        get_time_series_output_filename(get_base_output_filename(participant, session, EMG_POSITIONS[0], 0, 0)),
        get_feedback_output_filename(get_base_output_filename(participant, session, EMG_POSITIONS[0], 0, 0)),
    ])

# Classes
class CV2Video:
    def __init__(self, container: tkinter.Label, filename_or_index: str | int, api_preference: int, flipped: bool, width: int | None, height: int | None, use_fps_delay: bool, playback_speed: float = 1, frame_number: int = 0, use_threading: bool = False, looping: bool = False):
        self.container = container
        self.filename_or_index = filename_or_index
        self.api_preference = api_preference
        self.flipped = flipped
        self.width = width
        self.height = height
        self.use_fps_delay = use_fps_delay
        self.playback_speed = playback_speed
        self.frame_number = frame_number
        self.use_threading = use_threading
        self.looping = looping

        self._frame_collector: threading.Thread | multiprocessing.Process | None = None
        self._frame: cv2.typing.MatLike | None = None
        self._image: PIL.ImageTk.PhotoImage | None = None
        self._image_needs_update: bool = False

        self._frame_receiver: multiprocessing.connection.Connection | None = None
        self._frame_sender: multiprocessing.connection.Connection | None = None

        if self._is_main():
            self.container.bind("<Configure>", func=lambda _: self.set_image_dirty(), add=True)

            (self._frame_receiver, self._frame_sender) = multiprocessing.Pipe(duplex=False)

            if isinstance(self.filename_or_index, str):
                self._collect_first_frame()
                self._frame = self._first_frame
                self.set_image_dirty()


    def play(self):
        if self._frame_collector is None:
            if self.use_threading:
                self._frame_collector = threading.Thread(
                    target=self._collect_frames, 
                    args=(self._frame_sender, ),
                    daemon=True
                )
            else:
                self._frame_collector = multiprocessing.Process(
                    target=self._collect_frames, 
                    args=(self._frame_sender, ),
                    daemon=True
                )
            self._frame_collector.start()
            self.container.event_generate(sequence=VIDEO_PLAY_EVENT)

    def pause(self):
        if self._frame_collector is not None:
            if self.use_threading:
                thread: threading.Thread = self._frame_collector
                self._frame_collector = None
                thread.join()
            else:
                process: multiprocessing.Process = self._frame_collector
                process.terminate()
                process.close()
                process.join()
                self._frame_collector = None

            self.container.event_generate(sequence=VIDEO_PAUSE_EVENT)
            self._frame = self._first_frame
            self.set_image_dirty()

    def toggle_play_pause(self):
        if self._frame_collector is None:
            self.play()
        else:
            self.pause()

    def reset(self):
        self.pause()
        self.frame_number = 0

    def update(self) -> bool:
        reached_end: bool = False
        while self._frame_receiver.poll():
            frame = self._frame_receiver.recv()
            if frame is not None:
                self._on_frame_received(frame)
            else:
                reached_end = True
        if self._image_needs_update:
            self._update_image()
        return not reached_end
    
    def set_image_dirty(self) -> None:
        self._image_needs_update = True

    def _on_frame_received(self, frame: cv2.typing.MatLike) -> None:
        self.frame_number += 1
        self._frame = frame
        self._image_needs_update = True

    def _collect_first_frame(self):
        """Collects the first frame."""
        try:
            capture = self._create_capture()
            success, frame = capture.read()
            if success:
                self._first_frame = frame
        finally:
            capture.release()

    def _collect_frames(self, sender: multiprocessing.connection.PipeConnection):
        """Continuously collects frames. Should be executed on a seperate process."""
        try:
            capture = self._create_capture()

            if self.use_fps_delay:
                duration_per_frame = 1 / (capture.get(cv2.CAP_PROP_FPS) or 1) / self.playback_speed
                next_frame_time = time.time()
            while not sender.closed and (not self.use_threading or self._frame_collector is not None):
                success, frame = capture.read()
                if success:
                    sender.send(frame)
                elif self.looping:
                    capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    sender.send(None)
                    break
                if self.use_fps_delay:
                    next_frame_time += duration_per_frame
                    duration_to_next_frame = next_frame_time - time.time()
                    if duration_to_next_frame > 0:
                        time.sleep(duration_to_next_frame)
        finally:
            capture.release()

    def _create_capture(self) -> cv2.VideoCapture:
        capture = cv2.VideoCapture(self.filename_or_index, apiPreference=self.api_preference)
        if self.width is not None:
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        if self.height is not None:
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        if self.frame_number > 0:
            capture.set(cv2.CAP_PROP_POS_FRAMES, self.frame_number)
        return capture

    def _update_image(self) -> None:
        self._image_needs_update = False
        if self._frame is not None:
            optimal_size = self._get_optimal_size()
            image = self._frame
            if self.flipped:
                image = cv2.flip(image, 1)
            image = cv2.resize(image,optimal_size)
            image = cv2.cvtColor(image,cv2.COLOR_BGR2RGBA)
            image = PIL.Image.fromarray(image)
            image = PIL.ImageTk.PhotoImage(image)
            self._image = image
        else:
            self._image = None
        self.container.configure(image=self._image)

    def _get_optimal_size(self) -> tuple[int, int]:
        max_width = self.container.winfo_width()
        max_height = self.container.winfo_height()
        video_aspect_ratio = self._frame.shape[1] / self._frame.shape[0]
        target_aspect_ratio = max_width / max_height
        if video_aspect_ratio == target_aspect_ratio:
            return (max_width, max_height)
        elif video_aspect_ratio < target_aspect_ratio:
            return (math.ceil(max_height * video_aspect_ratio), max_height)
        else:
            return (max_width, math.ceil(max_width / video_aspect_ratio))

    def __reduce__(self) -> str | tuple[object, ...]:
        return (self.__class__, (None, self.filename_or_index, self.api_preference, self.flipped, self.width, self.height, self.use_fps_delay, self.playback_speed, self.frame_number, self.use_threading, self.looping))

    def __del__(self):
        if self._frame_collector is not None:
            self._frame_collector.join()
        if self._frame_receiver is not None:
            self._frame_receiver.close()
        if self._frame_sender is not None:
            self._frame_sender.close()
    
    def _is_main(self):
        return (self.use_threading and threading.current_thread().name == "MainThread") or (not self.use_threading and multiprocessing.current_process().name == "MainProcess")

class Webcam(CV2Video):
    def _on_frame_received(self, frame: cv2.typing.MatLike) -> None:
        global window, webcam_buffer
        if self._frame is None:
            window.event_generate(WEBCAM_FIRST_FRAME)
        if window.getvar(name="recording_active"):
            webcam_buffer.append(self._frame)
        return super()._on_frame_received(frame)
    
    def _update_image(self) -> None:
        global window
        if window.getvar("recording_active"):
            temp = self._frame
            border_size = 10
            self.width += border_size
            self.height += border_size
            self._frame = cv2.copyMakeBorder(temp, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT, None, (0, 0,255))
        super()._update_image()
        if window.getvar("recording_active"):
            self._frame = temp
            self.width -= border_size
            self.height -= border_size

if __name__ == '__main__':
    start_end_logger = TimeLogger("recording_app.py\tStart","recording_app.py\tDone\t{duration:.2f}")
    start_end_logger.start()
    window_exited = False

    with TimeLogger("Setup UI", "Done\t{duration:.2f}", separator="\t"):
        window = setup_ui()
    with TimeLogger("Setup Videos", "Done\t{duration:.2f}", separator="\t"):
        (webcam, previews) = setup_videos(window, 'root.videos.webcam.video', 'root.videos.preview.video')
        webcam.play()

    # Recording
    with TimeLogger("Setup Recording Variables", "Done"):
        recording_active_variable = tkinter.BooleanVar(master=window, name="recording_active", value=False)
        recording_start_variable = tkinter.Variable(master=window, name="recording_start", value=0.0)
        recording_active_variable.trace_add(mode="write", callback=lambda _, __, ___: print(recording_active_variable.get() and "Start Recording" or "Stop Recording"))
        recording_active_variable.trace_add(mode="write", callback=lambda _, __, ___: window.event_generate(recording_active_variable.get() and START_RECORDING_EVENT or STOP_RECORDING_EVENT))
        recording_active_variable.trace_add(mode="write", callback=lambda _, __, ___: recording_start_variable.set(value=recording_active_variable.get() and time.time() or recording_start_variable.get()))

        time_series_stream_info = next((stream_info for stream_info in pylsl.resolve_streams() if stream_info.name() == "OpenSignals"), None)
        time_series_inlet = time_series_stream_info is not None and pylsl.StreamInlet(time_series_stream_info) or None
        feedback_variable: tkinter.IntVar = tkinter.IntVar(window, name="feedback")
        feedback_variable.trace_add(mode="write", callback=lambda _, __, ___: window.event_generate(FEEDBACK_CHANGED_EVENT))
        time_series_buffer: list[list[float]] = []
        webcam_buffer: list[list[int]] = []
        window.bind(sequence=START_RECORDING_EVENT, func=lambda _: (print("Clear Time Series"), time_series_buffer.clear()), add=True)
        window.bind(sequence=START_RECORDING_EVENT, func=lambda _: webcam_buffer.clear(), add=True)
        window.bind(sequence=NEXT_LABEL_EVENT, func=lambda _: feedback_variable.set(-1), add=True)

        if time_series_inlet is None:
            tkinter.messagebox.showerror(message="No OpenSignals stream found\nPlease restart the app")
        elif time_series_inlet.channel_count-1 != len(tsml.CHANNELS):
            tkinter.messagebox.showerror(message=f"Wrong number of OpenSignal channels.\nGot: {time_series_inlet.channel_count-1}\nExpected: {len(tsml.CHANNELS)}\nPlease restart the app")

    # Indentifier
    with TimeLogger("Setup Identifier", "Done", separator="\t"):
        participant_value = tkinter.simpledialog.askstring(title="Participant", prompt="Enter the participant identifier:\t\t", parent=window) or 'test'
        emg_positioning_value = ask_selection(question="Which EMG positioning is used?", values=EMG_POSITIONS, title="EMG Positioning", master=window, font=FEEDBACK_QUESTION_FONT)
        session_value = next(i for i in range(tsml.RECORDING_APP_MAX_SESSION_NUMBER) if not does_session_exist(participant=participant_value, session=i))

        participant_variable = tkinter.StringVar(master=window, name="participant", value=participant_value)
        emg_positioning_variable = tkinter.StringVar(master=window, name="emg_positioning", value=emg_positioning_value)
        emg_positioning_switched_variable = tkinter.BooleanVar(master=window, name="emg_switched", value=False)
        session_variable = tkinter.IntVar(master=window, name="session", value=session_value)
        trial_variable = tkinter.IntVar(master=window, name="trial", value=0)
        label_variable = tkinter.IntVar(master=window, name="label", value=0)
        label_variable.trace_add(mode="write", callback= lambda _, __, ___:  window.event_generate(sequence=NEXT_LABEL_EVENT))
        window.event_generate(sequence=NEXT_LABEL_EVENT)

    # Main Loop
    print("Start Main Loop")
    window.state("zoomed")
    window.deiconify()
    if session_variable.get() == 0:
        tkinter.messagebox.showinfo(title="Instructions", message=tsml.RECORDING_APP_INSTRUCTIONS)
    while not window_exited:
        update_recording()
        webcam.update()
        if not previews[window.getvar("label")].update():
            previews[window.getvar("label")].reset()
        window.update()
    
    start_end_logger.end()