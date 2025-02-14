import glob
import os
import pathlib

import pandas
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score

import tsml
import utils


def get_title(filename: str, accuracy: float) -> str:
    parts = utils.get_filename_parts(filename)
    if filename.startswith("cvp") or (
        "pd" in parts and (parts["pd"] is True or parts["pd"] == "yes")
    ):
        return f"Person-Dependent Cross Validation: {accuracy:.2%}"
    else:
        return f"Person-Independent Cross Validation: {accuracy:.2%}"


def get_annotation(filename: str) -> str:
    return filename


def create_barplot(
    title: str,
    annotation: str,
    labels: list[str],
    values: list[float],
    ylabel: str,
    filename: str,
) -> None:
    pass


def create_confusion_matrix(
    title: str,
    annotation: str,
    labels: list[str],
    predictions: list[str],
    filename: str,
) -> None:
    pass


if __name__ == "__main__":
    os.makedirs(tsml.IMAGES_DIRECTORY, exist_ok=True)

    cross_validations = glob.glob(tsml.CROSS_VALIDATION_DIRECTORY, "*.csv")
    for filename in cross_validations:
        print(pathlib.Path(filename).stem)

        output_directory = os.path.join(
            tsml.IMAGES_DIRECTORY,
            pathlib.Path(filename).stem,
        )

        data = pandas.read_csv(filename)
        accuracy = accuracy_score(data[tsml.LABEL_COLUMN], data[tsml.PREDICTION_COLUMN])

        title = get_title(filename, accuracy)
        annotation = get_annotation(filename)

        labels = sorted(data[tsml.LABEL_COLUMN].unique())
        accuracies_labels = sorted(
            {
                label: accuracy_score(
                    y_true=l_data[tsml.LABEL_COLUMN],
                    y_pred=l_data[tsml.PREDICTION_COLUMN],
                )
                for label in labels
                if (l_data := data[data[tsml.LABEL_COLUMN] == label]) is not None
            }.items(),
            key=lambda x: x[1],
        )
        create_barplot(
            title=title,
            annotation=annotation,
            labels=[a[0] for a in accuracies_labels],
            values=[a[1] for a in accuracies_labels],
            ylabel="",
            filename=os.path.join(output_directory, "labels_bar"),
        )
        create_confusion_matrix(
            title=title,
            annotation=annotation,
            labels=data[tsml.LABEL_COLUMN],
            predictions=data[tsml.PREDICTION_COLUMN],
            filename=os.path.join(output_directory, "labels_cm"),
        )
