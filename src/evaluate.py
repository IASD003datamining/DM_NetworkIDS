import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import (accuracy_score, average_precision_score,
                             confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score)
from sklearn.preprocessing import label_binarize


def _scores(model, X):
    """Probability if available, otherwise decision_function, otherwise None."""
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)
    if hasattr(model, "decision_function"):
        return model.decision_function(X)
    return None


def fpr_fnr(y_true, y_pred, n_classes):
    """Macro-averaged false positive and false negative rates (one-vs-rest)."""
    cm = confusion_matrix(y_true, y_pred, labels=range(n_classes))
    fprs, fnrs = [], []
    for i in range(n_classes):
        tp = cm[i, i]
        fn = cm[i].sum() - tp
        fp = cm[:, i].sum() - tp
        tn = cm.sum() - tp - fn - fp
        if (tp + fn) > 0:
            fnrs.append(fn / (tp + fn))
        if (fp + tn) > 0:
            fprs.append(fp / (fp + tn))
    return float(np.mean(fprs)), float(np.mean(fnrs))