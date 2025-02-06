import glob
import os
import pathlib

import matplotlib.text
import pandas
from matplotlib import pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score

import tsml
import utils


def get_annotation(filename: str) -> str:
    parts = utils.get_filename_parts(filename)
    annotation = (
        f"Familiarity: {'fa' in parts and parts['fa'] or 'all'} - "
        f"Person Dependent: {parts['pd']} - Model: {parts['mo']} - "
        f"Window Size: {parts['ws'] != 'all' and parts['ws'] or "Full Length"}"
    )
    return annotation


def get_title(filename: str) -> str:
    parts = utils.get_filename_parts(filename)
    if "pd" not in parts or parts["pd"] == "no":
        return "Person-Independent Cross-Validation"
    else:
        return "Person-Dependent Cross-Validation"


def create_confusion_matrix(
    title: str,
    annotation: str,
    data: pandas.DataFrame,
    label_column: str = tsml.LABEL_COLUMN,
    prediction_column: str = tsml.PREDICTION_COLUMN,
) -> ConfusionMatrixDisplay:
    y_true = data[label_column]
    y_pred = data[prediction_column]

    labels = sorted(y_true.unique())
    confusion_matrix = ConfusionMatrixDisplay.from_predictions(
        labels=labels,
        y_pred=y_pred,
        y_true=y_true,
        normalize="true",
        values_format=".0%",
    )
    confusion_matrix.im_.set_clim(0, 1)
    confusion_matrix.ax_.set_title(title + f" - {accuracy_score(y_true, y_pred): .2%}")
    confusion_matrix.ax_.annotate(
        text=annotation,
        xy=(0.5, 0),
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

    return confusion_matrix


def create_barplot(title: str, annotation: str, labels: list[str], values: list[float], ylabel: str):
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

    return barplot


if __name__ == "__main__":

    os.makedirs(tsml.IMAGES_DIRECTORY, exist_ok=True)

    annotations = utils.load_annotations()
    p_t_to_word = annotations.groupby(['participant', 'trial']).groups

    for filename in glob.glob(os.path.join(tsml.CROSS_VALIDATION_DIRECTORY, "*.csv")):
        print(pathlib.Path(filename).stem)

        title = get_title(filename)
        annotation = get_annotation(filename)

        output_directory = os.path.join(tsml.IMAGES_DIRECTORY, pathlib.Path(filename).stem)
        os.makedirs(output_directory, exist_ok=True)
        parts = utils.get_filename_parts(filename)
        base_filename = os.path.join(output_directory, "")

        data = pandas.read_csv(filepath_or_buffer=filename)

        words = pandas.Series([
            annotations.iloc[
                p_t_to_word[
                    (int(data.iloc[i][tsml.PARTICIPANT_COLUMN]), int(data.iloc[i][tsml.TRIAL_COLUMN]))
                ]
            ]['word'].iloc[0]
            for i in range(len(data))
        ])
        words_unique = words.unique()
        accuracies_words = sorted(
            {
                word: accuracy_score(
                    y_true=w_data[tsml.LABEL_COLUMN],
                    y_pred=w_data[tsml.PREDICTION_COLUMN],
                )
                for word in words_unique
                if (w_data := data[words == word]) is not None
            }.items(),
            key=lambda x: x[1],
        )
        barplot_words = create_barplot(
            title=title,
            annotation=annotation,
            labels=[a[0] for a in accuracies_words],
            values=[a[1] for a in accuracies_words],
            ylabel="Word"
        )
        output_filename = base_filename + "words_bar.svg"
        plt.gcf().savefig(fname=output_filename)
        plt.close()
        print("\t", output_filename)
        continue

        # for category in sorted(data[tsml.LABEL_COLUMN].unique()):
        #    data_category = data[data[tsml.LABEL_COLUMN] == category]
        #    print(
        #        category,
        #        f"{accuracy_score(data_category[tsml.LABEL_COLUMN], data_category[tsml.PREDICTION_COLUMN]):.2%}",
        #    )

        cm = create_confusion_matrix(title=title, annotation=annotation, data=data)
        output_filename = base_filename + "category_confusion.svg"
        cm.figure_.savefig(fname=output_filename, bbox_inches="tight")
        plt.close(cm.figure_)
        print("\t", output_filename)

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
        barplot_participants = create_barplot(
            title=title,
            annotation=annotation,
            labels=[a[0] for a in accuracies_labels],
            values=[a[1] for a in accuracies_labels],
            ylabel="Participant"
        )
        output_filename = base_filename + "category_bar.svg"
        plt.gcf().savefig(fname=output_filename)
        plt.close()
        print("\t", output_filename)

        participants = sorted(data[tsml.PARTICIPANT_COLUMN].unique())
        accuracies_participants = sorted(
            {
                participant: accuracy_score(
                    y_true=l_data[tsml.LABEL_COLUMN],
                    y_pred=l_data[tsml.PREDICTION_COLUMN],
                )
                for participant in participants
                if (l_data := data[data[tsml.PARTICIPANT_COLUMN] == participant]) is not None
            }.items(),
            key=lambda x: x[1],
        )
        barplot_participants = create_barplot(
            title=title,
            annotation=annotation,
            labels=[a[0] for a in accuracies_participants],
            values=[a[1] for a in accuracies_participants],
            ylabel="Participant"
        )
        output_filename = base_filename + "participants_bar.svg"
        plt.gcf().savefig(fname=output_filename)
        plt.close()
        la = [a[0] for a in accuracies_participants]
        v = [a[1] for a in accuracies_participants]
        m = max(v)
        print("\t", output_filename, "\t", f"{m:.2}", la[v.index(m)])


