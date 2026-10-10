import json
import os
import re
from typing import Any

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Configure these in your .env file if your API runs somewhere else.
CHAT_API_URL = os.getenv("CHAT_API_URL", "http://localhost:8000/ai_respones")
PARTS_API_URL = os.getenv(
    "PARTS_API_URL", "http://localhost:8000/ai_agent_respones")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "180"))

st.set_page_config(
    page_title="AI PC Builder",
    page_icon="🖥️",
    layout="wide",
)

st.title("🖥️ AI PC Builder")
st.caption(
    "Chat with the builder on the left; inspect the suggested PC parts on the right.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "parts" not in st.session_state:
    st.session_state.parts = []
if "parts_raw" not in st.session_state:
    st.session_state.parts_raw = ""
if "last_error" not in st.session_state:
    st.session_state.last_error = ""


def stream_api_text(url: str, parameter_name: str, value: str):
    """Yield decoded text from a FastAPI StreamingResponse (text/plain)."""
    with requests.post(
        url,
        params={parameter_name: value},
        stream=True,
        timeout=(10, REQUEST_TIMEOUT),
    ) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            if chunk:
                # requests may return bytes despite decode_unicode=True.
                if isinstance(chunk, bytes):
                    chunk = chunk.decode("utf-8", errors="replace")
                yield chunk


def collect_api_text(url: str, parameter_name: str, value: str) -> str:
    """Collect a streamed endpoint response into one string."""
    return "".join(stream_api_text(url, parameter_name, value)).strip()


def extract_json_candidate(text: str) -> Any:
    """Parse JSON from plain JSON or a Markdown ```json fenced block."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    # First try the whole response.
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Then try the first JSON object/array embedded in prose.
    starts = [i for i in (cleaned.find("{"), cleaned.find("[")) if i >= 0]
    if not starts:
        raise ValueError("No JSON object or array was found in the response.")
    start = min(starts)
    for end in range(len(cleaned), start, -1):
        candidate = cleaned[start:end].strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    raise ValueError(
        "The response contains JSON-like text, but it could not be parsed.")


def find_parts(payload: Any) -> list[dict]:
    """Accept common response shapes and normalize part fields for the UI."""
    if isinstance(payload, dict):
        # Common direct response: {"parts": [...]}
        if isinstance(payload.get("parts"), list):
            raw_parts = payload["parts"]
        # Sometimes the model wraps JSON in a content/message field.
        else:
            raw_parts = None
            for key in ("content", "response", "output", "result", "message"):
                value = payload.get(key)
                if isinstance(value, str):
                    try:
                        return find_parts(extract_json_candidate(value))
                    except ValueError:
                        continue
            # A single part object can also be returned.
            if any(key in payload for key in ("pc-part-name", "name", "part_name", "title")):
                raw_parts = [payload]
            if raw_parts is None:
                # Support nested {"model": {"messages": [...]}}-like data.
                model = payload.get("model")
                if isinstance(model, dict):
                    messages = model.get("messages", [])
                    for message in reversed(messages if isinstance(messages, list) else []):
                        content = message.get("content") if isinstance(
                            message, dict) else getattr(message, "content", None)
                        if isinstance(content, str):
                            try:
                                return find_parts(extract_json_candidate(content))
                            except ValueError:
                                continue
                return []
    elif isinstance(payload, list):
        raw_parts = payload
    else:
        return []

    normalized = []
    for item in raw_parts:
        if not isinstance(item, dict):
            continue
        name = (
            item.get("pc-part-name")
            or item.get("name")
            or item.get("part_name")
            or item.get("title")
            or "PC component"
        )
        image = item.get("image") or item.get(
            "image_url") or item.get("image_url")
        description = item.get("description") or item.get(
            "details") or item.get("specifications") or ""
        price = item.get("price") or item.get(
            "estimated_price") or item.get("displayed_price")
        link = (
            item.get("shopping-link")
            or item.get("shop_link")
            or item.get("product_url")
            or item.get("url")
            or item.get("link")
        )
        normalized.append({
            "name": str(name),
            "image": str(image) if image else "",
            "description": str(description),
            "price": str(price) if price is not None else "",
            "link": str(link) if link else "",
        })
    return normalized


def show_parts(parts: list[dict]):
    if not parts:
        st.info("No structured parts were found yet. Ask the builder to recommend a PC, then check that the parts endpoint returns JSON with a `parts` array.")
        return

    for part in parts:
        with st.container(border=True):
            left, right = st.columns([1, 2], gap="medium")
            with left:
                if part["image"].startswith(("https://", "http://")):
                    st.image(part["image"], use_container_width=True)
                else:
                    st.markdown("🧩")
            with right:
                st.markdown(f"**{part['name']}**")
                if part["price"]:
                    st.markdown(f"**Price:** {part['price']}")
                if part["description"]:
                    st.write(part["description"])
                if part["link"].startswith(("https://", "http://")):
                    st.link_button(
                        "View product", part["link"], use_container_width=False)


with st.sidebar:
    st.subheader("API settings")
    st.code(f"Chat:  {CHAT_API_URL}\nParts: {PARTS_API_URL}", language="text")
    st.caption(
        "The FastAPI endpoints should accept query parameters named `input` and `user_input`, respectively.")
    if st.button("Clear chat and parts", use_container_width=True):
        st.session_state.messages = []
        st.session_state.parts = []
        st.session_state.parts_raw = ""
        st.session_state.last_error = ""
        st.rerun()

chat_col, parts_col = st.columns([1, 1.1], gap="large")

with chat_col:
    st.subheader("💬 Chat with your PC builder")
    chat_history = st.container(height=520)
    with chat_history:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    prompt = st.chat_input("Example: Build a gaming PC under ₹80,000")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_history:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                answer_slot = st.empty()
                try:
                    answer = st.write_stream(
                        stream_api_text(CHAT_API_URL, "input", prompt))
                    if not isinstance(answer, str):
                        answer = str(answer or "")
                    answer = answer.strip()
                    if not answer:
                        answer = "The chat endpoint returned an empty response."
                    answer_slot.markdown(answer)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer})

                    # Pass both the original request and the chat response to the parts agent
                    # so it does not lose the requested budget/use case.
                    agent_input = (
                        f"User's original PC-building request:\n{prompt}\n\n"
                        f"Chat agent response:\n{answer}\n\n"
                        "Use this context to find/recommend the relevant PC parts. "
                        "Return the parts as JSON with a top-level 'parts' array. "
                        "Each part should include pc-part-name, image, description, price, and shopping-link when available."
                    )
                    with st.spinner("Finding parts and product links..."):
                        raw_parts_response = collect_api_text(
                            PARTS_API_URL, "user_input", agent_input
                        )
                    st.session_state.parts_raw = raw_parts_response
                    try:
                        parts_payload = extract_json_candidate(
                            raw_parts_response)
                        st.session_state.parts = find_parts(parts_payload)
                    except ValueError:
                        st.session_state.parts = []
                        st.session_state.last_error = (
                            "The parts agent responded, but its output was not valid JSON. "
                            "Its raw response is available in the Parts panel."
                        )
                    else:
                        st.session_state.last_error = ""
                    st.rerun()
                except requests.RequestException as exc:
                    error_message = (
                        f"Could not reach the API: {exc}\n\n"
                        "Check that FastAPI is running and the endpoint URLs in the sidebar/.env are correct."
                    )
                    answer_slot.error(error_message)
                    st.session_state.last_error = error_message
                except Exception as exc:
                    error_message = f"Unexpected error: {exc}"
                    answer_slot.error(error_message)
                    st.session_state.last_error = error_message

with parts_col:
    st.subheader("🧩 Recommended PC parts")
    st.caption("Part cards are populated from the second endpoint's response.")
    if st.session_state.last_error:
        st.warning(st.session_state.last_error)
    show_parts(st.session_state.parts)

    with st.expander("View raw parts-agent response"):
        if st.session_state.parts_raw:
            st.code(st.session_state.parts_raw, language="json")
        else:
            st.caption("No parts-agent response yet.")
