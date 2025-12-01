import os
import json
import logging


def _invoke_bedrock(prompt: str) -> str:
    """Invoke AWS Bedrock runtime and return the textual output.

    Requires:
      - boto3 available in runtime
      - BEDROCK_MODEL_ID environment variable set
    """
    try:
        import boto3
    except Exception:
        logging.error("boto3 is required for Bedrock calls. Add boto3 to requirements.")
        raise

    model_id = os.getenv("BEDROCK_MODEL_ID")
    if not model_id:
        raise ValueError("BEDROCK_MODEL_ID environment variable must be set for Bedrock provider")

    client = boto3.client("bedrock-runtime")
    payload = json.dumps({"input": prompt}).encode("utf-8")
    resp = client.invoke_model(modelId=model_id, body=payload, contentType="application/json")
    body_bytes = resp["body"].read()

    # Try to decode JSON, else return raw text
    try:
        data = json.loads(body_bytes)
    except Exception:
        try:
            return body_bytes.decode("utf-8")
        except Exception:
            return str(body_bytes)

    # Heuristic extraction of text from common keys
    for candidate in ("output", "outputs", "results", "result", "completion", "completions", "text"):
        if candidate in data:
            val = data[candidate]
            if isinstance(val, list) and val:
                first = val[0]
                if isinstance(first, dict) and "content" in first:
                    return first["content"]
                if isinstance(first, str):
                    return first
            if isinstance(val, dict) and "content" in val:
                return val["content"]
            if isinstance(val, str):
                return val

    # fallback: return JSON string
    return json.dumps(data)


def query_llm(prompt: str) -> str:
    """Query AWS Bedrock for an LLM completion and return the textual result.

    This function only supports Bedrock. It will raise ValueError if
    the `BEDROCK_MODEL_ID` environment variable is not set.
    """
    # Only Bedrock is supported
    return _invoke_bedrock(prompt)
