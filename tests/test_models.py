import os


def test_churn_model_exists():

    assert os.path.exists(
        "models/churn_model.pkl"
    )