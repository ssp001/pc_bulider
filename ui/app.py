
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/ai_agent_respones"

st.set_page_config(
    page_title="AI Search Agent",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 AI Search Agent")
st.caption("Chat with your AI agent in real time.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def stream_response(user_input: str):
    with requests.post(
        API_URL,
        params={"user_input": user_input},
        stream=True,
        timeout=(5, 180),
    ) as response:
        response.raise_for_status()

        for chunk in response.iter_content(
            chunk_size=128,
            decode_unicode=True,
        ):
            if chunk:
                yield chunk


# Chat input
if prompt := st.chat_input("Ask your AI agent..."):

    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            answer = st.write_stream(stream_response(prompt))

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

        except requests.RequestException as error:
            st.error(f"API error: {error}")
