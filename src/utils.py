import time
import tkinter, tkinter.ttk

class TimeLogger():
    def __init__(self, start_message: str | None, end_message: str | None, separator: str = "\n") -> None:
        self._start_message = start_message
        self._end_message = end_message
        self._separator = separator

        self._start_time = None
        self._end_time = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.end()

    def start(self, **kwargs):
        self._start_time = time.time()
        if self._start_message:
            print(self._start_message.format(start_time = self._start_time, **kwargs), end=self._separator, flush=True)

    def end(self, **kwargs):
        self._end_time = time.time()
        if self._end_message:
            duration = self._end_time - self._start_time
            print(self._end_message.format(start_time=self._start_time, end_time=self._end_time, duration=duration, **kwargs))

def ask_selection(question: str, values: list[str], title: str, font: "tkinter.font._FontDescription", master: tkinter.Tk | None = None) -> str:
    
    dialog = tkinter.Toplevel(master=master)
    dialog.title(title)
    dialog.update_idletasks()
    if master:
        master.eval(f'tk::PlaceWindow {str(dialog)} center')

    tkinter.Label(dialog, text=question, font=font).grid(row=0, column=0, padx=5, pady=5, columnspan=len(values))

    selected: str = None
    def on_select(selected: str):
        selected = selected
        dialog.destroy()

    for i, choice in enumerate(values):
        tkinter.ttk.Button(dialog, text=str(choice), command=lambda c=choice: on_select(c)).grid(row = 1, column=i, padx=5, pady=5)

    dialog.wait_window()
    return selected
