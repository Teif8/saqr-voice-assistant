from openai import OpenAI
from dotenv import load_dotenv
import os

# تحميل المتغيرات
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# ذاكرة صقر
conversation_history = []

def ask_saqr(user_message):

    global conversation_history

    # حفظ كلام المستخدم
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    # نخلي آخر 10 رسائل فقط
    conversation_history = conversation_history[-10:]

    # برومبت صقر
    system_prompt = """
أنت صقر.

شاب سعودي عمره 24.
تتكلم باللهجة السعودية النجدية بشكل طبيعي جدًا.
وتفهم الأسماء السعودية صح.
إذا المستخدم قال اسمه احفظه بالحرف بدون تغيير.
لا تغيّر الأسماء أو تتوقعها.

لا تستخدم الفصحى أبدًا.

ردودك:
- قصيرة
- طبيعية
- كأنك خوي المستخدم
- لا تسولف كثير
- رد بسرعة وبعفوية

تستخدم كلمات مثل:
هلا
ابشر
يا بعدي
ولا يهمك
تم
ايه
شف

ممنوع:
- بالطبع
- يسعدني
- كيف أساعدك
- أهلًا بك
- الأسلوب الرسمي
- الكلام الروبوتي
- لا تخمن الأسماء
- لا تغير أسماء الناس

إذا أحد قال:
السلام عليكم

قل:
وعليكم السلام ارحب حياك الله
"""

    # إرسال الطلب
    response = client.chat.completions.create(
        model="gpt-4o-mini",

        messages=[
            {
                "role": "system",
                "content": system_prompt
            }
        ] + conversation_history
    )

    # الرد
    reply = response.choices[0].message.content

    # حفظ رد صقر
    conversation_history.append({
        "role": "assistant",
        "content": reply
    })

    return reply