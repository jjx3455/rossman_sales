import numpy as np
import pandas as pd
import datetime as dt

from data_cleaning import DataCleaning

from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor

from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline

from typing import List, Dict, Tuple

MODELS = [RandomForestRegressor, XGBRegressor]


def rmspe(preds: np.array, actuals: np.array) -> float:
    # As provided as finale metric, DO NOT MODIFY
    """ As provided - calculates the root mean square percentage error """
    preds = preds.reshape(-1)
    actuals = actuals.reshape(-1)
    assert preds.shape == actuals.shape
    return 100 * np.linalg.norm((actuals - preds) / actuals) / np.sqrt(preds.shape[0])


def define_pipelines(store, cleaning_settings, rf_settings, xg_settings) -> Tuple[Pipeline]:

    pipe_rf = Pipeline([
        (
            'scaler', MinMaxScaler()
        ),
        (
            'model', RandomForestRegressor(
                n_estimators=rf_settings['n_estimators'],
                max_depth=rf_settings['max_depth'],
                random_state=rf_settings['random_state'],
                n_jobs=rf_settings['n_jobs'],
            )
        ),
    ])

    pipe_xg = Pipeline([
        ('scaler', MinMaxScaler()),
        ('model', XGBRegressor(
            n_estimators=xg_settings['n_estimators'],
            max_depth=xg_settings['max_depth'],
            random_state=xg_settings['random_state'],
            n_jobs=xg_settings['n_jobs'],
        )
        ),
    ])

    return (pipe_rf, pipe_xg)


def split_validation(df: pd.DataFrame, year: int, month: int, day: int) -> Tuple[pd.DataFrame]:
    val_from = dt.date(year, month, day)
    val_msk = pd.to_datetime(df.loc[:, 'Date']).dt.date < val_from

    train = df.loc[val_msk, :]
    val = df.loc[~val_msk, :]

    X_train = train.drop(columns=['Sales'])
    y_train = train.loc[:, ['Sales']]
    X_val = val.drop(columns=['Sales'])
    y_val = val.loc[:, ['Sales']]

    return (X_train, y_train, X_val, y_val)


def evaluate_models(models: Tuple[object], X_val: pd.DataFrame, y_val: pd.DataFrame) -> List[Dict]:
    metrics = []
    for model in models:
        metric = {}
        print(X_val.shape)
        y_hat = model.predict(X_val)
        metric['model'] = type(model['model'])
        # TODO: is the feature order really correct?
        metric['feat_importance'] = sorted(
            list(
                zip(
                    list(X_val.columns),
                    list(model['model'].feature_importances_.round(2))
                )
            ),
            key=lambda x: x[1],
            reverse=True
        )
        metric['rmspe'] = round(rmspe(y_hat, y_val.to_numpy()), 2)
        metric['prediction'] = y_hat
        metrics.append(metric.copy())

    return metrics


def features_drop1(pipes, X_train, y_train, X_val, y_val):
    for pipe in pipes:
        scores = {}
        for feature1 in X_train.columns:
            X_train_drop1 = X_train.drop(columns=[feature1])
            X_val_drop1 = X_val.drop(columns=[feature1])
            pipe.fit(X_train_drop1, y_train)
            y_hat = pipe.predict(X_val_drop1)
            scores[feature1] = round(rmspe(y_hat, y_val.to_numpy()), 2)
        print(pipe)
        print(scores)


def feature_permutation(pipes, X_train, y_train, X_val, y_val):
    n_features = X_train.columns
    pass


def grid_search(X_train, y_train, X_val, y_val, rf_sets, xg_sets):
    for key in rf_sets.keys():
        for setting in rf_sets[key]:
            pass


def single_run(pipes, X_train, y_train, X_val, y_val):

    for pipe in pipes:
        pipe.fit(X_train, y_train)
    print('')
    print('Training performance:')
    training_metrics = evaluate_models(
        pipes, X_train, y_train)

    print(
        'Mean as Baseline (RMSPE)',
        rmspe(np.full_like(y_train, np.mean(
            y_train)), y_train.to_numpy())
    )

    for metric in training_metrics:
        print('')
        for key, values in metric.items():
            print(key, values)

    print('')
    print('Validation performance:')
    validation_metrics = evaluate_models(pipes, X_val, y_val)

    print(
        'Mean as Baseline (RMSPE)',
        rmspe(np.full_like(y_val, np.mean(
            y_train)), y_val.to_numpy())
    )

    for metric in validation_metrics:
        print('')
        for key, values in metric.items():
            print(key, values)


def single_run2(pipes, X_train, y_train, X_val, y_val, X_train_full, X_val_full):

    for pipe in pipes:
        pipe.fit(X_train, y_train)
    print('')
    print('Training performance:')
    training_metrics = evaluate_models(
        pipes, X_train, y_train)

    print(
        'Mean as Baseline (RMSPE)',
        rmspe(np.full_like(y_train, np.mean(
            y_train)), y_train.to_numpy())
    )

    for metric in training_metrics:
        print('')
        for key, values in metric.items():
            print(key, values)

    print('')
    print('Validation performance:')
    validation_metrics = evaluate_models(pipes, X_val, y_val)

    print(
        'Mean as Baseline (RMSPE)',
        rmspe(np.full_like(y_val, np.mean(
            y_train)), y_val.to_numpy())
    )

    for metric in validation_metrics:
        print('')
        for key, values in metric.items():
            print(key, values)

    X_train.loc[:, 'Date'] = pd.to_datetime(X_train_full.loc[:, 'Date'])
    X_val.loc[:, 'Date'] = pd.to_datetime(X_val_full.loc[:, 'Date'])

    return X_train, y_train, X_val, y_val, training_metrics, validation_metrics


# def evaluation_stuff():
#     metrics = []

#     for pipe in pipes:
#         pipe.fit(X_train, y_train)
#     print('')
#     print('Training performance:')
#     training_metrics = evaluate_models(
#         pipes, X_train, y_train)

#     print(
#         'Mean as Baseline (RMSPE)',
#         rmspe(np.full_like(y_train, np.mean(
#             y_train)), y_train.to_numpy())
#     )

#     for metric in training_metrics:
#         print('')
#         for key, values in metric.items():
#             print(key, values)

#     print('')
#     print('Validation performance:')
#     validation_metrics = evaluate_models(pipes, X_val, y_val)

#     print(
#         'Mean as Baseline (RMSPE)',
#         rmspe(np.full_like(y_val, np.mean(
#             y_train)), y_val.to_numpy())
#     )

#     for metric in validation_metrics:
#         print('')
#         for key, values in metric.items():
#             print(key, values)


#     return X_train, y_train, X_val, y_val, metrics
