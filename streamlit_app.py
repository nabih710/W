import streamlit as str
from google import genai
from google.genai import types

# 1. הגדרות בסיסיות של העמוד והצגת כותרת
st.set_page_config(page_title="סימולציית הנחיה", page_icon="🤖", layout="centered")
st.title("🤖 סימולציית הנחיה אינטראקטיבית")

# הוראות מערכת קבועות לסימולציה (System Instruction)
SYSTEM_INSTRUCTION = """
You are an expert psychological simulator and relaxation guide. 
Your goal is to guide the user through an adaptive guided imagery simulation based on their responses.
Always respond in Hebrew. Maintain a calm, supportive, and professional tone.
"""

# 2. שליפת מפתח ה-API ואתחול הלקוח החדש של גוגל
if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
    # העברת המפתח ישירות לפרמטר api_key תומכת בצורה מלאה במפתחות ה-AQ החדשים
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("מפתח ה-API חסר. אנא הגדר את GEMINI_API_KEY ב-Secrets של Streamlit.")
    st.stop()

# 3. ניהול זיכרון השיחה (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []

# הצגת היסטוריית ההודעות על המסך
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. קליטת קלט מהמשתמש והרצת הסימולציה
if user_input := st.chat_input("כתוב כאן את תגובתך..."):
    # הצגת הודעת המשתמש במסך
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # שמירה בהיסטוריית הצ'אט
    st.session_state.messages.append({"role": "user", "content": user_input})

    # פנייה למודל Gemini לקבלת תגובה
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # בניית מבנה ההיסטוריה בצורה המתאימה לספרייה החדשה
            contents = []
            for msg in st.session_state.messages:
                # הפיכת תפקיד ה-assistant ל-model בהתאם לדרישות ה-API
                role = "model" if msg["role"] == "assistant" else "user"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg["content"])]
                    )
                )

            # קריאה למודל היציב
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION
                )
            )
            
            # הצגת תגובת המודל
            ai_response = response.text
            message_placeholder.markdown(ai_response)
            
            # שמירה בהיסטוריית הצ'אט
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except Exception as e:
            message_placeholder.error("אירעה שגיאה בתקשורת עם השרת החדש.")
            st.info(f"פרטי השגיאה הטכנית: {str(e)}")
