import glob
import os
import pathlib

import pandas
from sklearn.metrics import accuracy_score

import tsml
import utils


def is_person_dependent(filename: str) -> bool:
    if filename.startswith("cvp"):
        return True
    elif filename.startswith("cvi"):
        return False
    else:
        parts = utils.get_filename_parts(filename)
        return "pd" in parts and (parts["pd"] is True or parts["pd"] == "yes")


def get_title(filename: str, accuracy: float) -> str:
    if is_person_dependent(filename):
        return f"Person-Dependent Cross Validation: {accuracy:.2%}"
    else:
        return f"Person-Independent Cross Validation: {accuracy:.2%}"


def get_annotation(filename: str) -> str:
    return pathlib.Path(filename).stem


def create_label_images(
    title: str,
    annotation: str,
    data: pandas.DataFrame,
    output_directory: str,
    filename_suffix: str,
):
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

    output_filename = os.path.join(
        output_directory,
        f"labels_bar{filename_suffix}.svg",
    )
    utils.create_barplot(
        title=title,
        annotation=annotation,
        labels=[a[0] for a in accuracies_labels],
        values=[a[1] for a in accuracies_labels],
        ylabel="Action Unit",
        output_filename=output_filename,
    )

    output_filename = os.path.join(
        output_directory,
        f"labels_cm{filename_suffix}.svg",
    )
    utils.create_confusion_matrix(
        title=title,
        annotation=annotation,
        y_true=data[tsml.LABEL_COLUMN],
        y_pred=data[tsml.PREDICTION_COLUMN],
        output_filename=output_filename,
    )


def create_participant_barplot(
    title: str,
    annotation: str,
    data: pandas.DataFrame,
    output_directory: str,
):

    participants = sorted(data[tsml.PARTICIPANT_COLUMN].unique())
    accuracies_participants = sorted(
        {
            participant: accuracy_score(
                y_true=l_data[tsml.LABEL_COLUMN],
                y_pred=l_data[tsml.PREDICTION_COLUMN],
            )
            for participant in participants
            if (l_data := data[data[tsml.PARTICIPANT_COLUMN] == participant])
            is not None
        }.items(),
        key=lambda x: x[1],
    )

    utils.create_barplot(
        title=title,
        annotation=annotation,
        labels=[a[0] for a in accuracies_participants],
        values=[a[1] for a in accuracies_participants],
        ylabel="Participant",
        output_filename=os.path.join(output_directory, "participants_bar.svg"),
    )


if __name__ == "__main__":
    cross_validations = glob.glob(
        os.path.join(tsml.CROSS_VALIDATION_DIRECTORY, "*.csv")
    )
    for filename in cross_validations:
        print(pathlib.Path(filename).stem)

        output_directory = os.path.join(
            tsml.IMAGES_CV_DIRECTORY,
            pathlib.Path(filename).stem,
        )
        os.makedirs(output_directory, exist_ok=True)

        data = pandas.read_csv(filename)

        # images for all participants
        accuracy = accuracy_score(
            y_true=data[tsml.LABEL_COLUMN],
            y_pred=data[tsml.PREDICTION_COLUMN],
        )
        title = get_title(filename, accuracy)
        annotation = get_annotation(filename)
        create_label_images(
            title=title,
            annotation=annotation,
            data=data,
            output_directory=output_directory,
            filename_suffix="",
        )
        create_participant_barplot(
            title=title,
            annotation=annotation,
            data=data,
            output_directory=output_directory,
        )

        # images for each participant
        for participant in data[tsml.PARTICIPANT_COLUMN].unique():
            output_directory_p = os.path.join(output_directory, "participants")
            os.makedirs(output_directory_p, exist_ok=True)
            data_p = data[data[tsml.PARTICIPANT_COLUMN] == participant]
            accuracy_p = accuracy_score(
                y_true=data_p[tsml.LABEL_COLUMN],
                y_pred=data_p[tsml.PREDICTION_COLUMN],
            )
            title_p = get_title(filename, accuracy_p)

            create_label_images(
                title=title_p,
                annotation=annotation,
                data=data_p,
                output_directory=output_directory_p,
                filename_suffix=f"_{participant}",
            )
