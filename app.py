import json
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import requests
import streamlit as st

API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL_ID = "meta-llama/Llama-3.2-1B-Instruct"
CHAT_DIR = Path("chats")
MEMORY_PATH = Path("memory.json")


def load_memory():
    if not MEMORY_PATH.exists():
        return {}
    try:
        return json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_memory(memory):
    with MEMORY_PATH.open("w", encoding="utf-8") as handle:
        json.dump(memory, handle, ensure_ascii=False, indent=2)


def merge_memory(current, update):
    merged = dict(current)
    for key, value in update.items():
        if value in (None, "", [], {}):
            continue
        if isinstance(value, list):
            existing = merged.get(key, [])
            if not isinstance(existing, list):
                existing = [existing]
            merged[key] = sorted(set(existing + value))
        elif isinstance(value, dict):
            existing = merged.get(key, {})
            if not isinstance(existing, dict):
                existing = {}
            merged[key] = {**existing, **value}
        else:
            merged[key] = value
    return merged


def build_system_prompt(memory):
    if not memory:
        return "You are a helpful assistant."
    return (
        "You are a helpful assistant. Personalize responses using the user memory "
        f"below:\n{json.dumps(memory, ensure_ascii=False)}"
    )


def extract_memory(user_message, hf_token):
    headers = {"Authorization": f"Bearer {hf_token}"}
    extraction_prompt = (
        "Given this user message, extract any personal traits or preferences as a JSON "
        "object with the following keys: name, preferred_language, interests, "
        "communication_style, favorite_topics, other_preferences. "
        "Return only valid JSON. If none, return {}.\n\nUser message:\n"
        f"{user_message}"
    )
    payload = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": extraction_prompt}],
        "max_tokens": 256,
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    except requests.exceptions.RequestException:
        return {}
    if response.status_code != 200:
        return {}
    try:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError):
        return {}


def save_chat(chat):
    CHAT_DIR.mkdir(parents=True, exist_ok=True)
    chat_path = CHAT_DIR / f"{chat['id']}.json"
    with chat_path.open("w", encoding="utf-8") as handle:
        json.dump(chat, handle, ensure_ascii=False, indent=2)


def delete_chat_file(chat_id):
    chat_path = CHAT_DIR / f"{chat_id}.json"
    if chat_path.exists():
        chat_path.unlink()


def load_chats():
    CHAT_DIR.mkdir(parents=True, exist_ok=True)
    chats = []
    for chat_file in sorted(CHAT_DIR.glob("*.json")):
        try:
            chat = json.loads(chat_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if "id" not in chat:
            chat["id"] = chat_file.stem
        chat.setdefault("title", "New Chat")
        chat.setdefault("created_at", datetime.now().strftime("%b %d, %I:%M %p"))
        chat.setdefault("messages", [])
        chats.append(chat)
    chats.sort(key=lambda c: c.get("created_at", ""), reverse=True)
    return chats

st.set_page_config(page_title="My AI Chat", layout="wide")
st.title("My AI Chat")

try:
    hf_token = st.secrets["HF_TOKEN"]
except (KeyError, FileNotFoundError):
    hf_token = ""

if not hf_token:
    st.error("Missing Hugging Face token. Add HF_TOKEN to .streamlit/secrets.toml.")
    st.stop()

if "chats" not in st.session_state:
    loaded = load_chats()
    if loaded:
        st.session_state.chats = loaded
        st.session_state.active_chat_id = loaded[0]["id"]
    else:
        first_chat_id = str(uuid4())
        new_chat = {
            "id": first_chat_id,
            "title": "New Chat",
            "created_at": datetime.now().strftime("%b %d, %I:%M %p"),
            "messages": [],
        }
        st.session_state.chats = [new_chat]
        st.session_state.active_chat_id = first_chat_id
        save_chat(new_chat)

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = (
        st.session_state.chats[0]["id"] if st.session_state.chats else None
    )

if "memory" not in st.session_state:
    st.session_state.memory = load_memory()

st.sidebar.header("Chats")
if st.sidebar.button("New Chat", use_container_width=True):
    new_chat_id = str(uuid4())
    new_chat = {
        "id": new_chat_id,
        "title": "New Chat",
        "created_at": datetime.now().strftime("%b %d, %I:%M %p"),
        "messages": [],
    }
    st.session_state.chats.insert(0, new_chat)
    st.session_state.active_chat_id = new_chat_id
    save_chat(new_chat)
    st.rerun()

chat_list = st.sidebar.container(height=360, border=True)
for chat in st.session_state.chats:
    is_active = chat["id"] == st.session_state.active_chat_id
    label = f"{'▶ ' if is_active else ''}{chat['title']}"
    col1, col2 = chat_list.columns([0.86, 0.14])
    if col1.button(label, key=f"select_{chat['id']}", use_container_width=True):
        st.session_state.active_chat_id = chat["id"]
        st.rerun()
    col1.caption(chat["created_at"])
    if col2.button("✕", key=f"delete_{chat['id']}", use_container_width=True):
        st.session_state.chats = [
            c for c in st.session_state.chats if c["id"] != chat["id"]
        ]
        delete_chat_file(chat["id"])
        if st.session_state.active_chat_id == chat["id"]:
            st.session_state.active_chat_id = (
                st.session_state.chats[0]["id"] if st.session_state.chats else None
            )
        st.rerun()

with st.sidebar.expander("User Memory", expanded=True):
    if st.button("Clear Memory", use_container_width=True):
        st.session_state.memory = {}
        save_memory(st.session_state.memory)
        st.rerun()
    st.json(st.session_state.memory)

active_chat = next(
    (c for c in st.session_state.chats if c["id"] == st.session_state.active_chat_id),
    None,
)

if active_chat is None:
    st.info("No chat selected. Create a new chat to get started.")
    st.stop()

for message in active_chat["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Type a message and press Enter")

if user_input:
    active_chat["messages"].append({"role": "user", "content": user_input})
    if active_chat["title"] == "New Chat":
        active_chat["title"] = user_input.strip()[:28] or "New Chat"
    save_chat(active_chat)

    with st.chat_message("user"):
        st.write(user_input)

    headers = {"Authorization": f"Bearer {hf_token}"}
    system_prompt = build_system_prompt(st.session_state.memory)
    payload = {
        "model": MODEL_ID,
        "messages": [{"role": "system", "content": system_prompt}] + active_chat["messages"],
        "max_tokens": 256,
        "stream": True,
    }

    with st.chat_message("assistant"):
        placeholder = st.empty()
        streamed_text = ""
        try:
            response = requests.post(
                API_URL, headers=headers, json=payload, stream=True, timeout=60
            )
        except requests.exceptions.RequestException as exc:
            st.error(f"Request failed: {exc}")
        else:
            if response.status_code != 200:
                st.error(f"API error {response.status_code}: {response.text}")
            else:
                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    if line.startswith("data: "):
                        data = line[6:]
                        if data.strip() == "[DONE]":
                            break
                        try:
                            event = json.loads(data)
                            delta = event["choices"][0]["delta"]
                            token = delta.get("content")
                        except (KeyError, IndexError, TypeError, json.JSONDecodeError):
                            continue
                        if token:
                            streamed_text += token
                            placeholder.write(streamed_text)
                            time.sleep(0.02)

                if streamed_text:
                    active_chat["messages"].append(
                        {"role": "assistant", "content": streamed_text}
                    )
                    save_chat(active_chat)

                    extracted = extract_memory(user_input, hf_token)
                    if extracted:
                        st.session_state.memory = merge_memory(
                            st.session_state.memory, extracted
                        )
                        save_memory(st.session_state.memory)
