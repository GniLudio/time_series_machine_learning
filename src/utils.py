import time

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

