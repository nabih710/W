import streamlit as st
from google import genai
from google.genai import types

# 1. הגדרות בסיסיות של העמוד והצגת כותרת
st.set_page_config(page_title="סימולציית הנחיה", page_icon="🤖", layout="centered")
st.title("🤖 סימולציית הנחיה אינטראקטיבית")

# הוראות מערכת קבועות לסימולציה (System Instruction) - כולל הנחיית הפתיחה
SYSTEM_INSTRUCTION = """
You are an expert psychological simulator and relaxation guide. 
Your goal is to guide the user through an adaptive guided imagery simulation based on their responses.
Always respond in Hebrew. Maintain a calm, supportive, and professional tone.

CRITICAL: Start the conversation immediately by welcoming the user, explaining briefly what the simulation is, and asking them about their current stress level or what kind of relaxing imagery they would like to explore today.
"""

# 2. שליפת מפתח ה-API ואתחול הלקוח החדש של גוגל
if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("מפתח ה-API חסר. אנא הגדר את GEMINI_API_KEY ב-Secrets של Streamlit.")
    st.stop()

# 3. ניהול זיכרון השיחה ואסטרטגיית הפתיחה האוטומטית
if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # ייצור אוטומטי של הודעת הפתיחה האסטרטגית מהמודל בלי לחכות למשתמש
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[types.Content(role="user", parts=[types.Part.from_text(text="התחל את הסימולציה והצג את שאלת הפתיחה שלך.")])],
            config={'system_instruction': SYSTEM_INSTRUCTION}
        )
        initial_bot_message = response.text
        st.session_state.messages.append({"role": "assistant", "content": initial_bot_message})
    except Exception as e:
        st.error(f"שגיאה באתחול הודעת הפתיחה: {e}")

# הצגת היסטוריית ההודעות (כולל הודעת הפתיחה שנוצרה)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. קליטת קלט מהמשתמש והמשך הסימולציה
if user_input := st.chat_input("כתוב כאן את תגובתך..."):
    # הצגת הודעת המשתמש במסך
    with st.chat_message("user"):
        st.markdown(user_input)
    
    st.session_state.messages.append({"role": "user", "content": user_input})

    # פנייה למודל Gemini לקבלת המשך התגובה
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # בניית מבנה ההיסטוריה לטובת המשכיות הדיאלוג
            contents = []
            for msg in st.session_state.messages:
                role = "model" if msg["role"] == "assistant" else "user"
                contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=contents,
                config={'system_instruction': SYSTEM_INSTRUCTION}
            )
            
            ai_response = response.text
            message_placeholder.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except Exception as e:
            message_placeholder.error("אירעה שגיאה במהלך הסימולציה.")
            st.write(f"טעות: {e}")
