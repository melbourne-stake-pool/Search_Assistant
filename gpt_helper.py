###### imports & setup #########################################################
import os
import json
import logging
from functools import lru_cache

try:
    import streamlit as st  # Optional: available at runtime in Streamlit
except Exception:
    st = None

from openai import OpenAI

logger = logging.getLogger(__name__)

###### api key resolution ######################################################
def _resolve_api_key() -> str:
    """
    Resolve the OpenAI API key from Streamlit secrets first, then environment.
    Raise a clear error if not found.
    """
    key = None
    if st is not None:
        # Use .get to avoid KeyError when running outside Streamlit
        key = st.secrets.get("OPENAI_API_KEY", None)
    if not key:
        key = os.getenv("OPENAI_API_KEY", None)
    if not key:
        raise RuntimeError(
            "OpenAI API key not found. Set it in Streamlit secrets "
            "as OPENAI_API_KEY or export OPENAI_API_KEY in the environment."
        )
    return key

###### client singleton ########################################################
@lru_cache(maxsize=1)
def _client() -> OpenAI:
    """
    Create a single OpenAI client for the process. Cached for reuse.
    """
    return OpenAI(api_key=_resolve_api_key())

###### gpt_api_call ############################################################
def gpt_api_call(prompt: str, 
                 model: str = "gpt-5-nano",  
                 system: str | None = None, 
                 response_format: str = "text",  # "text" | "json"
) -> dict:

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = _client().chat.completions.create(model=model, messages=messages)

    # Safely extract the content
    choice = resp.choices[0]
    msg = getattr(choice, "message", None)
    content = (getattr(msg, "content", "") or "").strip()

    if not content:
        logger.error("LLM returned empty content: %r", resp)
        raise RuntimeError("LLM returned no content to parse")

    out = {
        "content": content,
        "model": model,
        "usage": getattr(resp, "usage", None),
        "raw": resp,
        "json": None,
    }

    if response_format == "json":
        try:
            out["json"] = json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning("Failed to parse JSON from model output: %s", e)

    return out