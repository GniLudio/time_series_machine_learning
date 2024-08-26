import tkinter.dialog
import tkinter, tkinter.ttk, tkinter.simpledialog, tkinter.messagebox
import threading
import multiprocessing, multiprocessing.connection
import PIL, PIL.Image, PIL.ImageTk
import pylsl
import cv2
import os
import time
import math
import pandas
from utils import TimeLogger

import tsml

# STYLE
THEME = "clam"
INSTRUCTION_FONT = ("Helvetica", 12)
BUTTON_FONT = ("Helvetica", 12, "bold")
FEEDBACK_QUESTION_FONT = ("Helvetica", 12, "bold")
FEEDBACK_ANSWER_FONT = ("Arial", 10)

# Events
NEXT_LABEL_EVENT = '<<NextLabel>>'
VIDEO_PLAY_EVENT = "<<Play>>"
VIDEO_PAUSE_EVENT = "<<Pause>>"
START_RECORDING_EVENT = "<<StartRecording>>"
STOP_RECORDING_EVENT = "<<StopRecording>>"
FEEDBACK_CHANGED_EVENT = "<<FeedbackChanged>>"
WEBCAM_FIRST_FRAME = "<<WebcamFirstFrame>>"



# Setup
def setup_ui() -> tkinter.Tk:
    # Window
    window = tkinter.Tk()
    window.withdraw()
    window.minsize(width=720, height=480)
    window.title(string="TSML")
    window.grid_rowconfigure(index=0, weight=1)
    window.grid_columnconfigure(index=0, weight=1)
    window.protocol(name='WM_DELETE_WINDOW', func=on_exit)
    window.bind(
        sequence=NEXT_LABEL_EVENT, 
        func=lambda _: window.title(f"TSML - {window.getvar("participant")} - {window.getvar("session")} - {window.getvar("trial")} - {window.getvar("label")}"), 
        add=True
    )

    # Style
    style = tkinter.ttk.Style(master=window)
    style.theme_use(themename=THEME )
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

    preview_instruction = tkinter.ttk.Label(master=preview_container, name="instruction", justify="center", font=INSTRUCTION_FONT)
    preview_instruction.grid(row=1, column=0, padx=10, pady=10)
    window.bind(NEXT_LABEL_EVENT, func=lambda _: preview_instruction.configure(text=tsml.RECORDING_APP_PREVIEW_INSTRUCTION(window)), add=True)

    ### Seperator
    seperator_container = tkinter.ttk.Frame(master=video_container)
    seperator_container.grid_rowconfigure(index=0, weight=1)
    seperator_container.grid_columnconfigure(index=0, weight=1)
    video_container.add(child=seperator_container, weight=1)

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
    window.bind(sequence=STOP_RECORDING_EVENT, func=lambda _: start_recording_button.configure(text="DONE"), add=True)
    window.bind(sequence=WEBCAM_FIRST_FRAME, func=lambda _: window.bind(sequence=NEXT_LABEL_EVENT, func=lambda _: start_recording_button.configure(state="active", text="START"), add=True), add=True)

    ### Feedback
    feedback_container = tkinter.ttk.Frame(master=controls_container, name="feedback")
    feedback_container.grid(row=1, column=0, padx=10, pady=0)

    tkinter.ttk.Label(feedback_container, text="How well did you imitate this expression?", font=FEEDBACK_QUESTION_FONT).grid(row=0, column=0, columnspan=7)
    tkinter.ttk.Label(feedback_container, text="Very Bad", font=FEEDBACK_ANSWER_FONT).grid(row=1, column=0)
    for i in range(5):
        feedback_radiobutton = tkinter.ttk.Radiobutton(master=feedback_container, variable="feedback", value=i+1)
        feedback_radiobutton.grid(row=1, column=i+1)
    set_radiobutton_states = lambda state: [isinstance(widget, tkinter.ttk.Radiobutton) and widget.configure(state=state) for widget in feedback_container.winfo_children()]
    window.bind(sequence=NEXT_LABEL_EVENT, func=lambda e: set_radiobutton_states('disabled'), add=True)
    window.bind(sequence=STOP_RECORDING_EVENT, func=lambda e: set_radiobutton_states('normal'), add=True)
    tkinter.ttk.Label(master=feedback_container, text="Very Good", font=FEEDBACK_ANSWER_FONT).grid(row=1, column=6)

    ### Next Label
    next_button = tkinter.ttk.Button(controls_container, name="next_label", text="NEXT", command=next_label)
    next_button.grid(row=2, column=0, sticky="n", padx=10, pady=10)
    window.bind(sequence=NEXT_LABEL_EVENT, func=lambda _: next_button.configure(state="disabled"), add=True)
    window.bind(sequence=FEEDBACK_CHANGED_EVENT, func=lambda _: next_button.configure(state=window.getvar("feedback") > 0 and 'active' or 'disabled'), add=True)
    # TODO: Enable next button after feedback is given

    return window

def setup_videos(window: tkinter.Tk, webcam_path: str, preview_path: str) -> tuple['Webcam', dict[int, 'CV2Video']]:
    webcam_video = window.nametowidget(webcam_path)
    webcam = Webcam(
        container=webcam_video, 
        filename_or_index=0, 
        api_preference=cv2.CAP_ANY,
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
            width=None,
            height=None,
            use_fps_delay=True
        ) for i in range(tsml.NUMBER_OF_EXPRESSIONS)
    }

    return webcam, previews

# Actions
def toggle_preview():
    global window, previews
    print("Toggle Preview")
    previews[window.getvar("label")].toggle_play_pause()

def next_label():
    global window, previews, time_series_buffer, webcam_buffer, feedback_variable, webcam
    
    participant = window.getvar("participant")
    session = window.getvar("session")
    trial = window.getvar("trial")
    label = window.getvar("label")

    threading.Thread(
        target=save_recording, 
        daemon=False, 
        args=(
            participant, session, trial, label, 
            time_series_buffer, webcam_buffer, window.getvar("feedback")
        )
    ).start()

    time_series_buffer = []
    webcam_buffer = []
    window.setvar(name="feedback", value=0)

    if label+1 < tsml.NUMBER_OF_EXPRESSIONS:
        print("Next Label")
        window.setvar(name="label", value=label+1)
    else:
        next_session = tkinter.messagebox.askyesno(message="Do you want to continue?")
        if next_session:
            print("Next Trial")
            window.setvar(name="trial", value=trial+1)
            window.setvar(name="label", value=0)
        else:
            print("Didn't continue")
            on_exit()

def update_recording():
    global window, time_series_inlet, time_series_buffer

    if time_series_inlet is not None:
        if not window.getvar(name="recording_active"):
            time_series_inlet.flush()
        else:
            (samples, _) = time_series_inlet.pull_chunk()
            if samples is not None:
                time_series_buffer.extend(samples)

    if window.getvar("recording_active") and time.time() - window.getvar("recording_start") >= tsml.RECORDING_APP_EXPRESSION_DURATION:
        window.setvar(name="recording_active", value=False)
        
def save_recording(participant: str, session: int, trial: int, label: int, time_series_data: tsml.TimeSeriesBuffer, webcam_data: tsml.WebcamBuffer, feedback_data: int):
    print("Save Recording", participant, session, trial, label)

    base_filename = get_base_output_filename(participant=participant, session=session, trial=trial, label=label)

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

# Paths
def get_base_output_filename(participant: str, session: int, trial: int, label: int) -> str:
    return f"p{participant}_s{session}_t{trial}_l{label}"

def get_webcam_output_filename(filename: str) -> str:
    return os.path.join(tsml.RECORDING_WEBCAM_DIRECTORY, filename + ".avi")

def get_time_series_output_filename(filename: str) -> str:
    return os.path.join(tsml.RECORDING_TIMESERIES_DIRECTORY, filename + ".csv")

def get_feedback_output_filename(filename: str) -> str:
    return os.path.join(tsml.RECORDING_FEEDBACK_DIRECTORY, filename + ".txt")

def does_session_exist(participant: str, session: int) -> bool:
    return any(os.path.exists(filename) for filename in [
        get_webcam_output_filename(get_base_output_filename(participant, session, 0, 0)),
        get_time_series_output_filename(get_base_output_filename(participant, session, 0, 0)),
        get_feedback_output_filename(get_base_output_filename(participant, session, 0, 0)),
    ])

# Classes
class CV2Video:
    def __init__(self, container: tkinter.Label, filename_or_index: str | int, api_preference: int, width: int | None, height: int | None, use_fps_delay: bool, frame_number: int = 0):
        self.container = container
        self.filename_or_index = filename_or_index
        self.api_preference = api_preference
        self.width = width
        self.height = height
        self.use_fps_delay = use_fps_delay
        self.frame_number = frame_number

        self._frame_collector: multiprocessing.Process | None = None
        self._frame: cv2.typing.MatLike | None = None
        self._image: PIL.ImageTk.PhotoImage | None = None
        self._image_needs_update: bool = False

        if multiprocessing.current_process().name == "MainProcess":
            self.container.bind("<Configure>", func=lambda _: self.set_image_dirty(), add=True)

            (self._frame_receiver, self._frame_sender) = multiprocessing.Pipe(duplex=False)

            if isinstance(self.filename_or_index, str):
                self._collect_first_frame()
        else:
            self._frame_receiver = None
            self._frame_sender = None

    def play(self):
        if self._frame_collector is None:
            self._frame_collector = multiprocessing.Process(
                target=self._collect_frames, 
                args=(self._frame_sender, ),
                daemon=True
            )
            self._frame_collector.start()
            self.container.event_generate(sequence=VIDEO_PLAY_EVENT)

    def pause(self):
        if self._frame_collector is not None:
            self.container.event_generate(sequence=VIDEO_PAUSE_EVENT)
            self._frame_collector.terminate()
            self._frame_collector.join()
            self._frame_collector.close()
            self._frame_collector = None

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
                self._frame = frame
                self.set_image_dirty()
        finally:
            capture.release()

    def _collect_frames(self, sender: multiprocessing.connection.PipeConnection):
        """Continuously collects frames. Should be executed on a seperate process."""
        try:
            capture = self._create_capture()

            if self.use_fps_delay:
                duration_per_frame = 1 / (capture.get(cv2.CAP_PROP_FPS) or 1)
                next_frame_time = time.time()
            while not sender.closed:
                success, frame = capture.read()
                if success:
                    sender.send(frame)
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
            image = cv2.resize(self._frame,optimal_size)
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
        return (self.__class__, (None, self.filename_or_index, self.api_preference, self.width, self.height, self.use_fps_delay, self.frame_number))

    def __del__(self):
        if self._frame_collector is not None:
            self._frame_collector.terminate()
            self._frame_collector.join()
            self._frame_collector.close()
        if self._frame_receiver is not None:
            self._frame_receiver.close()
        if self._frame_sender is not None:
            self._frame_sender.close()

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
        time_series_buffer: tsml.TimeSeriesBuffer = []
        feedback_variable: tkinter.IntVar = tkinter.IntVar(window, name="feedback")
        webcam_buffer: tsml.WebcamBuffer = []

        feedback_variable.trace_add(mode="write", callback=lambda _, __, ___: window.event_generate(FEEDBACK_CHANGED_EVENT))

        if time_series_inlet is None:
            tkinter.messagebox.showerror(message="No OpenSignals stream found\nPlease restart the app")
        elif time_series_inlet.channel_count-1 != len(tsml.CHANNELS):
            tkinter.messagebox.showerror(message=f"Wrong number of OpenSignal channels.\nGot: {time_series_inlet.channel_count-1}\nExpected: {len(tsml.CHANNELS)}\nPlease restart the app")

    # Indentifier
    with TimeLogger("Setup Identifier", "Done", separator="\t"):
        participant_value = tkinter.simpledialog.askstring(title="Participant", prompt="Enter the participant identifier:\t\t", parent=window) or 'test'
        session_value = next(i for i in range(tsml.RECORDING_APP_MAX_SESSION_NUMBER) if not does_session_exist(participant=participant_value, session=i))

        participant = tkinter.StringVar(master=window, name="participant", value=participant_value)
        session = tkinter.IntVar(master=window, name="session", value=session_value)
        trial = tkinter.IntVar(master=window, name="trial", value=0)
        label = tkinter.IntVar(master=window, name="label", value=0)
        label.trace_add(mode="write", callback= lambda _, __, ___:  window.event_generate(sequence=NEXT_LABEL_EVENT))
        window.event_generate(sequence=NEXT_LABEL_EVENT)

    # Main Loop
    print("Start Main Loop")
    window.deiconify()
    window.state("zoomed")
    while not window_exited:
        update_recording()
        webcam.update()
        if not previews[label.get()].update():
            previews[label.get()].reset()
        window.update()
    
    start_end_logger.end()