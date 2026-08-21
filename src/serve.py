import sys
import os
import builtins
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3

# Hook xu ly unpickle tuong thich cho Python 3.14 tren EC2
try:
    import sklearn._loss._loss as loss_mod
except Exception:
    try:
        import sklearn._loss as loss_mod
    except Exception:
        loss_mod = None

if loss_mod is not None:
    sys.modules['_loss'] = loss_mod
    sys.modules['sklearn._loss._loss'] = loss_mod

    orig_import = builtins.__import__
    def hook_import(name, *args, **kwargs):
        if name == '_loss':
            return loss_mod
        return orig_import(name, *args, **kwargs)
    builtins.__import__ = hook_import

app = FastAPI()

ARTIFACT_BUCKET = os.environ.get("ARTIFACT_BUCKET", "income-lab-minh-2026")
AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
MODEL_KEY = "artifacts/current/model.joblib"
MODEL_PATH = os.path.expanduser("~/models/model.joblib")


def download_model():
    """
    Tai file model.joblib tu S3 ve may khi server khoi dong.
    """
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    s3 = boto3.client("s3", region_name=AWS_REGION)
    s3.download_file(ARTIFACT_BUCKET, MODEL_KEY, MODEL_PATH)
    print("Model da duoc tai xuong tu S3.")


download_model()
model = joblib.load(MODEL_PATH)


class ScoreRequest(BaseModel):
    features: list[float]


@app.get("/healthz")
def healthz():
    """
    Endpoint kiem tra suc khoe server.
    """
    return {"status": "ok"}


@app.post("/score")
def score(req: ScoreRequest):
    """
    Endpoint suy luan chinh.

    Dau vao : JSON {"features": [f1, f2, ..., f10]}
    Dau ra  : JSON {"prediction": <0|1>, "label": <"thu_nhap_thap"|"thu_nhap_cao">}

    Thu tu 10 dac trung:
        age, workclass, education_num, marital_status, occupation,
        relationship, sex, capital_gain, capital_loss, hours_per_week
    """
    if len(req.features) != 10:
        raise HTTPException(
            status_code=400,
            detail="Expected 10 features (adult income)"
        )

    pred = model.predict([req.features])[0]
    label = "thu_nhap_cao" if pred == 1 else "thu_nhap_thap"
    return {"prediction": int(pred), "label": label}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
