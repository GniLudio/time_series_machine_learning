import pandas
from sklearn.metrics import accuracy_score

import cross_validation

if __name__ == "__main__":
    filenames = [
        cross_validation.get_output_filename(do, None, 0, 'RandomForestClassifier', None, pd, fa)
        for pd in [True, False]
        for fa in ['both', 'yes']
        for do in ['all', 'fractal', 'spectral', 'temporal', 'statistical']
    ]
    # filenames = [
    #     cross_validation.get_output_filename("all", None, 0, 'RandomForestClassifier' + mo, None, pd, fa)
    #     for pd in [True, False]
    #     for fa in ['both', 'yes']
    #     for mo in ['', '6', '7']
    # ]
    # filenames = [
    #     cross_validation.get_output_filename("all", None, 0, 'RandomForestClassifier', None, pd, fa)
    #     for pd in [True, False]
    #     for fa in ['both', 'yes']
    # ]
    data = [pandas.read_csv(f) for f in filenames]
    best_participant = [
        sorted([
            (int(p), accuracy_score(df_p['Label'], df_p['Prediction']))
            for p in df['Participant'].unique()
            if (df_p := df[df['Participant'] == p]) is not None
        ], key=lambda x: -x[1])[0]
        for df in data
    ]
    worst_participant = [
        sorted([
            (int(p), accuracy_score(df_p['Label'], df_p['Prediction']))
            for p in df['Participant'].unique()
            if (df_p := df[df['Participant'] == p]) is not None
        ], key=lambda x: -x[1])[-1]
        for df in data
    ]
    accuracies = [
        *[accuracy_score(df['Label'], df['Prediction']) for df in data]
    ]

    labels = ['all', 'fractal', 'spectral', 'temporal', 'statistical']
    print(*labels)
    average = [0 for _ in labels]
    for i in range(0, len(accuracies)-len(labels)+1, len(labels)):
        print(filenames[i].split("\\")[-1][:-4].ljust(75), end="\t")
        for j in range(len(labels)):
            accuracy = best_participant[i+j][1]
            average[j] += accuracy
            print(f"{accuracy:.2%}", end=" ")
        print()
    print()
    for j in range(len(labels)):
        print(f"{(average[j] / len(accuracies) * len(labels)):.2%}", end=" ")