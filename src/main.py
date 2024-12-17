import subprocess
import os
import tkinter.simpledialog

participant = tkinter.simpledialog.askstring(title="Participant", prompt="Enter the participant identifier:\t\t") or 'test'

subprocess.run(["python", os.path.join("src", "recording_app.py"), "-pa", participant])