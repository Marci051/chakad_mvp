import gradio as gr
import requests
import json
import time
import os

system_prompt = {
    "role": "system",
    "content": """
تو یک مشاور درسی مهربان، دقیق و حرفه‌ای هستی. فقط به سوالات مرتبط با درس‌های دبیرستان مثل ریاضی، فیزیک، شیمی، زیست، هندسه، زبان فارسی، عربی و زبان انگلیسی و در زمینه مشاوره تحصیلی پاسخ می‌دهی.
اگر سوالی بی‌ربط بود، محترمانه بگو "من فقط در زمینه‌ی درس‌های مدرسه می‌تونم کمک کنم."
جواب‌هات فارسی روان و آموزشی باشه.
"""
}

def stream_bot(user_input, history, chat_state):
    chat_state.append({"role": "user", "content": user_input})

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer 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",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "chakad"
            },
            json={
                "model": "deepseek/deepseek-r1-0528:free",
                "messages": chat_state
            }
        )

        if response.status_code != 200:
            reply = f"خطا: وضعیت پاسخ API برابر {response.status_code} است.\nجزئیات: {response.text}"
        else:
            data = response.json()
            reply = data["choices"][0]["message"]["content"]

    except Exception as e:
        reply = f"خطا در برقراری ارتباط با API:\n{str(e)}"

    bot_response = ""
    for char in reply:
        bot_response += char
        time.sleep(0.01)
        yield "", history + [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": bot_response}
        ], chat_state


css = """
:root {
  --color-primary-500: #7B3FBF; /* بنفش */
  --color-primary-600: #6A36A8;
  --color-primary-700: #582E8C;
  --color-primary-800: #4A2673;
  --color-primary-900: #3D1E5A;
}

body {
  direction: rtl;
  font-family: Vazir, sans-serif;
  background-color: #fefcf8 !important;
}
textarea, .message, .markdown {
  direction: rtl !important;
  font-family: Vazir, sans-serif !important;
}
"""

with gr.Blocks(css=css, theme=gr.themes.Default()) as app:

    gr.Markdown("""
    <link href="https://cdn.fontcdn.ir/Font/Persian/Vazir/Vazir.css" rel="stylesheet">
    <p style='text-align:center;'>سوالات درسی‌تو از من بپرس 🌟</p>
    """)

    chatbot_ui = gr.Chatbot(label="چت درسی", type="messages")
    txt = gr.Textbox(placeholder="پیامت رو بنویس...", show_label=False)
    state = gr.State([system_prompt]) 

    txt.submit(stream_bot, inputs=[txt, chatbot_ui, state], outputs=[txt, chatbot_ui, state])

app.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))
