import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="סימולציית הנחיה", page_icon="🤖", layout="centered")
st.title("🤖 סימולציית הנחיה אינטראקטיבית")

SYSTEM_INSTRUCTION = """
You are an expert psychological simulator and relaxation guide. 
Your goal is to guide the user through an adaptive guided imagery simulation based on their responses.
Always respond in Hebrew. Maintain a calm, supportive, and professional tone.
"""

# התיקון הקריטי: הגדרה מפורשת של ה-API Key ללקוח
if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
    # שימוש בפרמטר מפורש לאימות מפתח
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("מפתח ה-API חסר. אנא הגדר את GEMINI_API_KEY ב-Secrets של Streamlit.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("כתוב כאן את תגובתך..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            # בניית היסטוריה תקינה
            contents = []
            for msg in st.session_state.messages:
                role = "model" if msg["role"] == "assistant" else "user"
                contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

            # קריאה למודל ללא הגדרות נוספות שעלולות לבלבל את האימות
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=contents,
                config={'system_instruction': SYSTEM_INSTRUCTION}
            )
            
            ai_response = response.text
            message_placeholder.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
        except Exception as e:
            message_placeholder.error("שגיאת אימות. אנא וודא שמפתח ה-API שלך תקין ב-Secrets.")
            st.write(f"טעות: {e}")
