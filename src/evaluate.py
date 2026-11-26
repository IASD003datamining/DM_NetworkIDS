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

def compute_metrics(model, X, y_true, n_classes):
    """Return a dict of metrics. y_true holds integer-encoded labels."""
    y_pred = model.predict(X)
    avg_kw = dict(zero_division=0)
    out = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision_macro": precision_score(y_true, y_pred, average="macro", **avg_kw),
        "recall_macro": recall_score(y_true, y_pred, average="macro", **avg_kw),
        "f1_macro": f1_score(y_true, y_pred, average="macro", **avg_kw),
        "f1_weighted": f1_score(y_true, y_pred, average="weighted", **avg_kw),
    }
    if n_classes == 2:
        out["precision"] = precision_score(y_true, y_pred, **avg_kw)
        out["recall"] = recall_score(y_true, y_pred, **avg_kw)
        out["f1"] = f1_score(y_true, y_pred, **avg_kw)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        out["fpr"] = fp / (fp + tn) if (fp + tn) else np.nan
        out["fnr"] = fn / (fn + tp) if (fn + tp) else np.nan
    else:
        out["fpr"], out["fnr"] = fpr_fnr(y_true, y_pred, n_classes)

    out["roc_auc"] = out["pr_auc"] = np.nan
    s = _scores(model, X)
    if s is not None:
        try:
            if n_classes == 2:
                s1 = s[:, 1] if s.ndim == 2 else s
                out["roc_auc"] = roc_auc_score(y_true, s1)
                out["pr_auc"] = average_precision_score(y_true, s1)
            elif np.allclose(s.sum(axis=1), 1.0, atol=1e-3):
                out["roc_auc"] = roc_auc_score(y_true, s, multi_class="ovr",
                                               average="macro")
                yb = label_binarize(y_true, classes=range(n_classes))
                out["pr_auc"] = average_precision_score(yb, s, average="macro")
        except ValueError:
            pass  # a class absent from y_true: AUC undefined, keep NaN
    return out, y_pred


def plot_confusion_matrix(y_true, y_pred, class_names, title, path):
    """Save a row-normalised confusion matrix (recall per class) with counts."""
    labels = range(len(class_names))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    norm = cm / np.maximum(cm.sum(axis=1, keepdims=True), 1)
    annot = np.array([[f"{norm[i, j]:.2f}\n({cm[i, j]})" for j in labels]
                      for i in labels])
    fig, ax = plt.subplots(figsize=(1.6 * len(class_names) + 2,) * 2)
    sns.heatmap(norm, annot=annot, fmt="", cmap="Blues", vmin=0, vmax=1,
                xticklabels=class_names, yticklabels=class_names, ax=ax)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(title)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)