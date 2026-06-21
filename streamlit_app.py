import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="סימולציית הנחיה", page_icon="🤖", layout="centered")
st.title("🤖 סימולציית הנחיה אינטראקטיבית")

SYSTEM_INSTRUCTION = """
You are an expert psychological simulator and relaxation guide. 
Your goal is to guide the user through an adaptive guided imagery simulation based on their responses.
Always respond in Hebrew. Maintain a calm, supportive, and professional tone.
"""

# הגדרת המפתח בספרייה הישנה
if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
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
            # אתחול המודל עם הוראות המערכת
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=SYSTEM_INSTRUCTION
            )
            
            # בניית היסטוריית שיחה בפורמט הישן
            history = []
            for msg in st.session_state.messages[:-1]:
                role = "model" if msg["role"] == "assistant" else "user"
                history.append({"role": role, "parts": [msg["content"]]})
            
            chat = model.start_chat(history=history)
            response = chat.send_message(user_input)
            
            ai_response = response.text
            message_placeholder.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
        except Exception as e:
            message_placeholder.error("אירעה שגיאה בתקשורת עם המודל.")
            st.write(f"פרטי השגיאה: {e}")
