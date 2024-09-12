import sklearn.calibration
import sklearn.discriminant_analysis
import sklearn.dummy
import sklearn.ensemble
import sklearn.gaussian_process
import sklearn.linear_model
import sklearn.model_selection
import sklearn.multiclass
import sklearn.multioutput
import sklearn.naive_bayes
import sklearn.neighbors
import sklearn.neural_network
import sklearn.semi_supervised
import sklearn.svm
import sklearn.tree
import sklearn.base

MODELS: dict[str, sklearn.base.BaseEstimator] = {
    'AdaBoost': lambda: sklearn.ensemble.AdaBoostClassifier(),
    'Bagging': lambda: sklearn.ensemble.BaggingClassifier(),
    'BernoulliNB': lambda: sklearn.naive_bayes.BernoulliNB(),
    'CalibratedClassifierCV': lambda: sklearn.calibration.CalibratedClassifierCV(),
    'CategoricalNB': lambda: sklearn.naive_bayes.CategoricalNB(),
    #'ClassifierChain': lambda: sklearn.multioutput.ClassifierChain(),
    'ComplementNB': lambda: sklearn.naive_bayes.ComplementNB(),
    'DecisionTreeClassifier': lambda: sklearn.tree.DecisionTreeClassifier(),
    'DummyClassifier': lambda: sklearn.dummy.DummyClassifier(),
    'ExtraTreeClassifier': lambda: sklearn.tree.ExtraTreeClassifier(),
    'ExtraTreesClassifier': lambda: sklearn.ensemble.ExtraTreesClassifier(),
    #'FixedThresholdClassifier': lambda: sklearn.model_selection.FixedThresholdClassifier(),
    'GaussianNB': lambda: sklearn.naive_bayes.GaussianNB(),
    'GaussianProcessClassifier': lambda: sklearn.gaussian_process.GaussianProcessClassifier(),
    'GradientBoostingClassifier': lambda: sklearn.ensemble.GradientBoostingClassifier(),
    'HistGradientBoostingClassifier': lambda: sklearn.ensemble.HistGradientBoostingClassifier(),
    'KNeighborsClassifier': lambda: sklearn.neighbors.KNeighborsClassifier(),
    'LabelPropagation': lambda: sklearn.semi_supervised.LabelPropagation(),
    'LabelSpreading': lambda: sklearn.semi_supervised.LabelSpreading(),
    'LinearDiscriminantAnalysis': lambda: sklearn.discriminant_analysis.LinearDiscriminantAnalysis(),
    'LinearSVC': lambda: sklearn.svm.LinearSVC(),
    'LogisticRegression': lambda: sklearn.linear_model.LogisticRegression(),
    'LogisticRegressionCV': lambda: sklearn.linear_model.LogisticRegressionCV(),
    'MLPClassifier': lambda: sklearn.neural_network.MLPClassifier(),
    #'MultiOutputClassifier': lambda: sklearn.multioutput.MultiOutputClassifier(),
    'MultinomialNB': lambda: sklearn.naive_bayes.MultinomialNB(),
    'NearestCentroid': lambda: sklearn.neighbors.NearestCentroid(),
    'NuSVC': lambda: sklearn.svm.NuSVC(),
    #'OneVsOneClassifier': lambda: sklearn.multiclass.OneVsOneClassifier(),
    #'OneVsRestClassifier': lambda: sklearn.multiclass.OneVsRestClassifier(),
    #'OutputCodeClassifier': lambda: sklearn.multiclass.OutputCodeClassifier(),
    'PassiveAggressiveClassifier': lambda: sklearn.linear_model.PassiveAggressiveClassifier(),
    'Perceptron': lambda: sklearn.linear_model.Perceptron(),
    'QuadraticDiscriminantAnalysis': lambda: sklearn.discriminant_analysis.QuadraticDiscriminantAnalysis(),
    'RadiusNeighborsClassifier': lambda: sklearn.neighbors.RadiusNeighborsClassifier(),
    'RandomForestClassifier': lambda: sklearn.ensemble.RandomForestClassifier(),
    'RidgeClassifier': lambda: sklearn.linear_model.RidgeClassifier(),
    'RidgeClassifierCV': lambda: sklearn.linear_model.RidgeClassifierCV(),
    'SGDClassifier': lambda: sklearn.linear_model.SGDClassifier(),
    'SVC': lambda: sklearn.svm.SVC(),
    #'StackingClassifier': lambda: sklearn.ensemble.StackingClassifier(),
    #'TunedThresholdClassifierCV': lambda: sklearn.model_selection.TunedThresholdClassifierCV(),
    #'VotingClassifier': lambda: sklearn.ensemble.VotingClassifier(),
}