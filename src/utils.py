import pathlib
import time
import matplotlib
from matplotlib import pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay


class TimeLogger:
    def __init__(
        self,
        start_message: str | None,
        end_message: str | None,
        separator: str = "\n",
    ) -> None:
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
            print(
                self._start_message.format(
                    start_time=self._start_time,
                    **kwargs,
                ),
                end=self._separator,
                flush=True,
            )

    def end(self, **kwargs):
        self._end_time = time.time()
        if self._end_message:
            duration = self._end_time - self._start_time
            print(
                self._end_message.format(
                    start_time=self._start_time,
                    end_time=self._end_time,
                    duration=duration,
                    **kwargs,
                )
            )


def get_filename_parts(filename: str) -> dict[str, str]:
    base_filename = pathlib.Path(filename).stem

    parts = {}
    for part in str(base_filename).split("_"):
        key, value = "-" in part and part.split("-") or (part, None)
        parts[key] = value

    return parts


def join_filename_parts(parts: dict[str, any]) -> str:
    return "_".join(
        (f"{key}-{value}") for key, value in parts.items() if value is not None
    )


def create_barplot(
    title: str,
    annotation: str,
    labels: list[str],
    values: list[float],
    ylabel: str,
    output_filename: str,
) -> None:

    barplot = plt.barh(
        y=list(range(len(labels))),
        width=values,
    )
    plt.gcf().set_size_inches(10, 10)
    plt.gcf().subplots_adjust(top=0.95, bottom=0.06)

    figure = plt.gcf()
    axis = figure.axes[0]
    axis.set_title(title)
    axis.set_xlim(xmin=0, xmax=1)
    axis.bar_label(barplot, fmt=" {:.2%}", fontsize=8)
    axis.set_yticks(ticks=list(range(len(labels))), labels=labels, fontsize=8)
    axis.set_ylabel(ylabel)
    axis.set_xticks(
        ticks=[0.01 * x for x in range(0, 110, 10)],
        labels=[f"{x}%" for x in range(0, 110, 10)],
    )

    axis.annotate(
        text=annotation,
        xy=(0.5, 0),
        xycoords="subfigure fraction",
        va="bottom",
        ha="center",
        fontsize=8,
    )

    plt.gcf().savefig(fname=output_filename)
    plt.close()


def create_confusion_matrix(
    title: str,
    annotation: str,
    y_true: list[str],
    y_pred: list[str],
    output_filename: str,
) -> None:

    labels = sorted(y_true.unique())
    confusion_matrix = ConfusionMatrixDisplay.from_predictions(
        labels=labels,
        y_pred=y_pred,
        y_true=y_true,
        normalize="true",
        values_format=".0%",
    )

    confusion_matrix.im_.set_clim(0, 1)
    confusion_matrix.ax_.set_title(title)
    confusion_matrix.ax_.annotate(
        text=annotation,
        xy=(0.5, 0.005),
        xycoords="subfigure fraction",
        va="bottom",
        ha="center",
        fontsize=6,
    )

    for y in range(len(confusion_matrix.text_)):
        for x in range(len(confusion_matrix.text_[y])):
            text: matplotlib.text.Text = confusion_matrix.text_[y][x]
            text.set_fontweight("bold")
            text.set_fontsize(9)
            confusion_matrix.ax_.text(
                x=text.get_position()[0],
                y=text.get_position()[1] + 0.2,
                s=str(((y_true == labels[y]) & (y_pred == labels[x])).sum()),
                verticalalignment="top",
                horizontalalignment="center",
                fontdict={
                    "family": text.get_fontfamily(),
                    "color": text.get_color(),
                    "weight": "normal",
                    "size": text.get_fontsize() - 2,
                },
            )

    confusion_matrix.figure_.savefig(
        fname=output_filename,
        bbox_inches="tight",
    )
    plt.close(confusion_matrix.figure_)
