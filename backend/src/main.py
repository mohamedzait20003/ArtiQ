from fastapi import FastAPI
from mangum import Mangum

app = FastAPI(title="Serverless FastAPI", version="0.1.0")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


# AWS Lambda handler
handler = Mangum(app)
