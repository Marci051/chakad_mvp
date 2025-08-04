import streamlit as st
import requests
import time

st.set_page_config(page_title="چکاد | همراه تحصیلی تو", layout="wide")

st.markdown("""
<style>
@import url('https://cdn.fontcdn.ir/Font/Persian/Vazir/Vazir.css');

html, body, [class*="css"] {
    font-family: 'Vazir', sans-serif;
    direction: rtl;
    background-color: #fefcf8;
}

.avatar-icon {
    position: fixed;
    top: 20px;
    left: 20px;
    background-color: #eee;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    z-index: 1000;
    box-shadow: 0 0 6px rgba(0,0,0,0.2);
}

.title-text {
    text-align: center;
    font-size: 20px;
    margin-top: 60px;
    color: #333;
}

.subtitle-text {
    text-align: center;
    font-size: 16px;
    margin-bottom: 30px;
    color: #777;
}

.chat-container {
    max-width: 700px;
    margin: 0 auto;
    padding: 1rem;
    padding-bottom: 200px;
}

.chat-history {
    max-height: 75vh;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.message {
    padding: 1rem;
    border-radius: 1rem;
    line-height: 2rem;
    white-space: pre-wrap;
    width: fit-content;
    max-width: 90%;
}

.user-msg {
    background-color: #dcf8c6;
    align-self: flex-end;
    text-align: right;
}

.bot-msg {
    background-color: #eeeeee;
    align-self: flex-start;
    text-align: right;
}

.chat-input {
    position: fixed;
    bottom: 0;
    right: 0;
    left: 0;
    background-color: #fff;
    padding: 1rem 2rem;
    box-shadow: 0 -1px 8px rgba(0,0,0,0.1);
    z-index: 1000;
}

.chat-input input {
    width: 100%;
    padding: 0.75rem;
    font-size: 16px;
    border-radius: 12px;
    border: 1px solid #ccc;
}

.chat-input button {
    margin-top: 0.5rem;
    width: 100%;
    padding: 0.75rem;
    font-size: 16px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 12px;
    cursor: pointer;
}
</style>
<div class="avatar-icon">👤</div>
""", unsafe_allow_html=True)

system_prompt = """
تو یک مشاور درسی مهربان، دقیق و حرفه‌ای هستی. فقط به سوالات مرتبط با درس‌های دبیرستان مثل ریاضی، فیزیک، شیمی، زیست، هندسه، زبان فارسی، عربی و زبان انگلیسی و در زمینه مشاوره تحصیلی پاسخ می‌دهی.
اگر سوالی بی‌ربط بود، محترمانه بگو "من فقط در زمینه‌ی درس‌های مدرسه می‌تونم کمک کنم."
جواب‌هات فارسی روان و آموزشی باشه.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    st.session_state.pending = False
    st.session_state.partial_response = ""

st.markdown('<div class="title-text">من چکاد هستم، دستیار درسی تو</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">هرچی دوست داری ازم بپرس...</div>', unsafe_allow_html=True)

st.markdown('<div class="chat-container"><div class="chat-history">', unsafe_allow_html=True)

for msg in st.session_state.messages[1:]:  # exclude system prompt
    role_class = "user-msg" if msg["role"] == "user" else "bot-msg"
    st.markdown(f'<div class="message {role_class}">{msg["content"]}</div>', unsafe_allow_html=True)

if st.session_state.pending:
    st.markdown(f'<div class="message bot-msg">{st.session_state.partial_response}</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

st.markdown('<div class="chat-input">', unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("پیام خود را بنویسید...", key="chat_input", label_visibility="collapsed")
    send_button = st.form_submit_button("📨 ارسال")

st.markdown('</div>', unsafe_allow_html=True)

if send_button and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.pending = True
    st.session_state.partial_response = ""
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer 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",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-r1-0528:free",
                "messages": st.session_state.messages
            }
        )
        reply = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        reply = f" خطایی رخ داد: {e}"

    response_placeholder = ""
    for ch in reply:
        response_placeholder += ch
        st.session_state.partial_response = response_placeholder
        time.sleep(0.015)
        st.experimental_rerun()

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.pending = False
    st.session_state.partial_response = ""
    st.rerun()
