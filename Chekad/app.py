import gradio as gr
import requests
import json
import time

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


with gr.Blocks(css="""
body { background-color: #fefcf8 !important; direction: rtl; font-family: Vazir, sans-serif; }
textarea, .message, .markdown { direction: rtl !important; font-family: Vazir, sans-serif !important; }
""", theme=gr.themes.Soft()) as app:

    gr.Markdown("""
    <link href="https://cdn.fontcdn.ir/Font/Persian/Vazir/Vazir.css" rel="stylesheet">
    <h1 style='text-align:center;'>چکاد | همراه تحصیلی تو</h1>
    <p style='text-align:center;'>سوالات درسی‌تو از من بپرس 🌟</p>
    """)

    chatbot_ui = gr.Chatbot(label="چت درسی", type="messages")
    txt = gr.Textbox(placeholder="پیامت رو بنویس...", show_label=False)
    state = gr.State([system_prompt]) 

    txt.submit(stream_bot, inputs=[txt, chatbot_ui, state], outputs=[txt, chatbot_ui, state])

app.launch()
