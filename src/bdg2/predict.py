"""Fit Ridge on train, predict test. StandardScaler because sqm and temp live on different scales."""
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from . import features, eval as ev


def fit_predict(train_df, test_df):
    """Returns (test preds frame, n_train, train_cv_rmse). The train score is the overfit check."""
    Xtr, ytr, _ = features.build(train_df)
    Xte, yte, te = features.build(test_df)
    model = make_pipeline(StandardScaler(), Ridge())
    model.fit(Xtr, ytr)
    train_cv_rmse = ev.cv_rmse(ytr, model.predict(Xtr))  # error on data it was fit on
    return te.assign(y=yte, yhat=model.predict(Xte)), len(ytr), train_cv_rmse
