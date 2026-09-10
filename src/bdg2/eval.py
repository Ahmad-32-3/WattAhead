"""RMSE and CV-RMSE (RMSE / mean test kWh). R2 is not a headline."""
import numpy as np
from sklearn.metrics import mean_squared_error


def rmse(y, yhat):
    return float(np.sqrt(mean_squared_error(y, yhat)))


def cv_rmse(y, yhat):
    m = float(np.mean(y))
    if m == 0:
        return float("nan")
    return rmse(y, yhat) / m


def score(pred):
    """pred: frame with y, yhat. -> (rmse, cv_rmse)."""
    return rmse(pred.y, pred.yhat), cv_rmse(pred.y, pred.yhat)
