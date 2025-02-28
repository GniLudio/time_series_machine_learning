import os
import pandas
from sklearn.metrics import accuracy_score

import tsml
import utils


def generate_comparison(
    title: str,
    annotation: str,
    data: dict[str, str],
    output_filename: str,
    sort_by_accuracy=True,
):
    data = {
        label: os.path.join(tsml.CROSS_VALIDATION_DIRECTORY, filename)
        for label, filename in data.items()
    }

    accuracies = list(
        {
            label: accuracy_score(
                y_true=data[tsml.LABEL_COLUMN],
                y_pred=data[tsml.PREDICTION_COLUMN],
            )
            for label, filepath in data.items()
            if (data := pandas.read_csv(filepath)) is not None
        }.items()
    )

    if sort_by_accuracy:
        accuracies.sort(key=lambda x: x[1])
    else:
        accuracies.reverse()

    output_filename = os.path.join(
        tsml.IMAGE_COMPARISONS_DIRECTORY,
        output_filename,
    )
    utils.create_barplot(
        title=title,
        annotation=annotation,
        labels=[a[0] for a in accuracies],
        values=[a[1] for a in accuracies],
        ylabel="",
        output_filename=output_filename,
    )
    print(output_filename)


if __name__ == "__main__":

    os.makedirs(tsml.IMAGE_COMPARISONS_DIRECTORY, exist_ok=True)
    generate_comparison(
        title="Window Size Comparison",
        annotation="Person Dependent - 20% Overlap - Random Forest",
        data={
            "100": "cvp_all_all_all_no_all_100_20_no_rf_all.csv",
            "200": "cvp_all_all_all_no_all_200_20_no_rf_all.csv",
            "400": "cvp_all_all_all_no_all_400_20_no_rf_all.csv",
            "800": "cvp_all_all_all_no_all_800_20_no_rf_all.csv",
            "1000": "cvp_all_all_all_no_all_1000_20_no_rf_all.csv",
        },
        output_filename="window_sizes.svg",
        sort_by_accuracy=False,
    ),

    generate_comparison(
        title="Window Overlap Comparison",
        annotation="Person Dependent - 400ms Window SIze - Random Forest",
        data={
            "0": "cvp_all_all_all_no_all_400_0_no_rf_all.csv",
            "5": "cvp_all_all_all_no_all_400_5_no_rf_all.csv",
            "10": "cvp_all_all_all_no_all_400_10_no_rf_all.csv",
            "15": "cvp_all_all_all_no_all_400_15_no_rf_all.csv",
            "20": "cvp_all_all_all_no_all_400_20_no_rf_all.csv",
            "25": "cvp_all_all_all_no_all_400_25_no_rf_all.csv",
            "50": "cvp_all_all_all_no_all_400_50_no_rf_all.csv",
        },
        output_filename="window_overlaps.svg",
        sort_by_accuracy=False,
    ),

    generate_comparison(
        title="Person-Independent Model Comparison",
        annotation="400ms Window Size - 20% Overlap",
        data={
            "SVC": "cvi-d_all-ws_400-wo_20-m_SVC-c_0.1.2.3.csv",
            "CalibratedCV": "cvi-d_all-ws_400-wo_20-m_CalibratedClassifierCV-c_0.1.2.3.csv",
            "MLP": "cvi-d_all-ws_400-wo_20-m_MLPClassifier-c_0.1.2.3.csv",
            "LinearSVC": "cvi-d_all-ws_400-wo_20-m_LinearSVC-c_0.1.2.3.csv",
            "Bagging": "cvi-d_all-ws_400-wo_20-m_Bagging-c_0.1.2.3.csv",
            "AdaBoost": "cvi-d_all-ws_400-wo_20-m_AdaBoost-c_0.1.2.3.csv",
            "Random Forest": "cvi-d_all-ws_400-wo_20-m_RandomForestClassifier-c_0.1.2.3.csv",
            "Decision Tree": "cvi-d_all-ws_400-wo_20-m_DecisionTreeClassifier-c_0.1.2.3.csv",
            "KNN": "cvi-d_all-ws_400-wo_20-m_KNeighborsClassifier-c_0.1.2.3.csv",
            "Gaussian NB": "cvi-d_all-ws_400-wo_20-m_GaussianNB-c_0.1.2.3.csv",
        },
        output_filename="cvi_models.svg",
    )

    generate_comparison(
        title="Person-Dependent Model Comparison",
        annotation="Person Dependent - 400ms Window Size - 20% Overlap",
        data={
            "gnb": "cvp_all_all_all_no_all_400_20_no_gnb_all.csv",
            "svm": "cvp_all_all_all_no_all_400_20_no_svm_all.csv",
            "rf": "cvp_all_all_all_no_all_400_20_no_rf_all.csv",
            "knn": "cvp_all_all_all_no_all_400_20_no_knn_all.csv",
        },
        output_filename="cvp_models.svg",
    )

    generate_comparison(
        title="Minimum Rating Comparison",
        annotation="Person Dependent - 400ms WIndow Size - 20% Overlap - Random Forest",
        data={
            "all": "cvp_all_all_all_no_all_400_20_no_rf_all.csv",
            "1": "cvp_all_all_all_no_1_400_20_no_rf_all.csv",
            "2": "cvp_all_all_all_no_2_400_20_no_rf_all.csv",
            "3": "cvp_all_all_all_no_3_400_20_no_rf_all.csv",
            "4": "cvp_all_all_all_no_4_400_20_no_rf_all.csv",
            "5": "cvp_all_all_all_no_5_400_20_no_rf_all.csv",
        },
        output_filename="minimum_ratings.svg",
        sort_by_accuracy=False,
    )

    generate_comparison(
        title="Folding Strategy Comparison",
        annotation="Person Dependent - 400ms Window Size - 20% Overlap - Random Forest",
        data={
            "Each Action Unit": "cvp_all_all_all_no_all_400_20_action_rf_all.csv",
            "Each Trial": "cvp_all_all_all_no_all_400_20_trial_rf_all.csv",
            "Each Session": "cvp_all_all_all_no_all_400_20_session_rf_all.csv",
            "None": "cvp_all_all_all_no_all_400_20_no_rf_all.csv",
        },
        output_filename="folding_strategies.svg",
    )

    generate_comparison(
        title="Good/Bad Half Comparison",
        annotation="Person Independent - 400ms Window Size - 20% Overlap - Random Forest - All Channels",
        data={
            "Bad": "cvi_do-all_ws-400_wo-20_mo-RandomForestClassifier_ch-0.1.2.3_de-no_half-bad.csv",
            "Good": "cvi_do-all_ws-400_wo-20_mo-RandomForestClassifier_ch-0.1.2.3_de-no_half-good.csv",
            "All": "cvi-d_all-ws_400-wo_20-m_RandomForestClassifier-c_0.1.2.3.csv",
        },
        output_filename="good_bad.svg",
    )
