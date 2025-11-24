import boto3
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

bedrock = boto3.client("bedrock-runtime", region_name="us-east-2")
MODEL_ID = "openai.gpt-oss-120b-1:0"


def _call_bedrock(prompt: str) -> str:
    """Call GPT-OSS via Bedrock and return the assistant's *raw* content string."""
    native_request = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": "You are a JSON-only responder."},
            {"role": "user", "content": prompt},
        ],
        "max_completion_tokens": 1024,
        "temperature": 0.2,
        "top_p": 0.9,
    }

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(native_request),
        accept="application/json",
        contentType="application/json",
    )

    body_bytes = response["body"].read()
    if not body_bytes:
        raise ValueError("Bedrock returned empty body")

    body_str = body_bytes.decode("utf-8")
    try:
        body_json = json.loads(body_str)
    except Exception:
        logger.error("Failed to parse Bedrock body as JSON: %s", body_str[:500])
        raise

    try:
        content = body_json["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        logger.error("Unexpected GPT-OSS response structure: %s", body_str[:500])
        raise e

    if not isinstance(content, str):
        raise TypeError("Expected GPT-OSS content to be a string")

    return content


def _extract_json_from_content(content: str) -> str:
    """Strip <reasoning> wrapper and extract JSON."""
    content = content.strip()

    if content.startswith("<reasoning>"):
        closing = content.find("</reasoning>")
        if closing != -1:
            content = content[closing + len("</reasoning>") :].strip()

    start = content.find("{")
    end = content.rfind("}")

    if start == -1 or end == -1 or end < start:
        logger.error("LLM did not return JSON. Raw content: %r", content[:500])
        raise ValueError("LLM response does not contain a JSON object")

    return content[start : end + 1].strip()


def query_llm(prompt: str) -> Any:
    """
    Call GPT-OSS once (no manual retries) and return parsed JSON.
    Bedrock performs its own retry logic internally.
    """
    raw_content = _call_bedrock(prompt).strip()
    logger.debug("GPT-OSS raw content (truncated): %s", raw_content[:200])

    json_str = _extract_json_from_content(raw_content)
    logger.debug("GPT-OSS cleaned JSON (truncated): %s", json_str[:200])

    return json.loads(json_str)
