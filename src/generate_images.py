import os
import glob
import pandas
import pathlib
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score
from matplotlib import pyplot as plt
import matplotlib.text
import numpy

import utils
import tsml

def create_confusion_matrix():
    pass

def get_annotation(filename: str) -> str:
    parts = utils.get_filename_parts(filename)
    annotation = f"Model: {parts['mo']} - Window Size: {parts['ws']} - Person Dependent: {parts['pd']} - Channels: {parts['ch']}"
    return annotation

def get_title(filename: str) -> str:
    stem = pathlib.Path(filename).stem
    if stem.startswith("cvp_"):
        return "Person-Dependent Cross-Validation"
    elif stem.startswith("cvi_"):
        return "Person-Independent Cross-Validation"
    
def create_confusion_matrix(title: str, annotation: str, y_true: list[any], y_pred: list[any]) -> ConfusionMatrixDisplay:
    confusion_matrix = ConfusionMatrixDisplay.from_predictions(
        labels=sorted(y_true.unique()),
        y_pred=y_pred,
        y_true=y_true,
        normalize='true',
        values_format='.2f'
    )
    confusion_matrix.im_.set_clim(0, 1)
    confusion_matrix.ax_.set_title(title + f" - {accuracy_score(y_true, y_pred): .2%}")
    confusion_matrix.ax_.annotate(
        text= annotation,
        xy=(0.5,0),
        xycoords='subfigure fraction', 
        va='bottom',
        ha='center',
        fontsize=6
    )
    confusion_matrix.figure_.tight_layout()
    confusion_matrix.ax_.set_xlabel("Prediction")
    confusion_matrix.ax_.set_ylabel("Reference")

    for y in range(len(confusion_matrix.text_)):
        for x in range(len(confusion_matrix.text_[y])):
            text: matplotlib.text.Text = confusion_matrix.text_[y][x]
            text.set_fontweight("bold")
            text.set_fontsize(9)
            confusion_matrix.ax_.text(
                x = text.get_position()[0],
                y = text.get_position()[1] + 0.2,
                s = "Asdf",
                verticalalignment = "top",
                horizontalalignment = "center",
                fontdict={
                    'family': text.get_fontfamily(),
                    'color': "grey",
                    'weight': 'normal',
                    'size': text.get_fontsize() - 2
                }
            )

    return confusion_matrix

def create_barplot(title: str, annotation: str, labels: list[str], values: list[float]):
    barplot = plt.barh(
        y = len(labels),
        width = values,
        tick_label = labels,
    )
    return barplot

if __name__ == "__main__":

    os.makedirs(tsml.IMAGES_DIRECTORY, exist_ok=True)

    for filename in glob.glob(os.path.join(tsml.CROSS_VALIDATION_DIRECTORY, "*", "*.csv")):
        print(pathlib.Path(filename).stem)
        output_directory = os.path.join(tsml.IMAGES_DIRECTORY, pathlib.Path(filename).stem)
        os.makedirs(output_directory, exist_ok=True)

        data = pandas.read_csv(filepath_or_buffer=filename)
        cm = create_confusion_matrix(
            title = get_title(filename), 
            annotation = get_annotation(filename),
            y_true=data[tsml.LABEL_COLUMN],
            y_pred=data[tsml.PREDICTION_COLUMN]
        )
        cm.figure_.savefig(fname=os.path.join(output_directory, 'confusion_matrix.png'), bbox_inches='tight', dpi=600)
        plt.close(cm.figure_)



