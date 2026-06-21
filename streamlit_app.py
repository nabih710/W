import streamlit as st
import google.generativeai as genai

# 1. הגדרת תצורת הדף - חייב להיות פקודת הסטרימליט הראשונה בקוד
st.set_page_config(page_title="סימולציית הרפיה אדפטיבית", layout="centered", initial_sidebar_state="collapsed")

# 2. שליפת מפתח ה-API בצורה מאובטחת מתוך ה-Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("מפתח ה-API חסר. אנא הגדר את GEMINI_API_KEY ב-Secrets של Streamlit.")
    st.stop()

# 3. הגדרת הנחיות המערכת (System Instruction) עבור המודל
SYSTEM_INSTRUCTION = """
You are an advanced, empathetic AI simulation designed by Nabia, specializing in positive psychology, mindfulness, and adaptive relaxation. Your goal is to guide the user through a customized imagery and relaxation session.

CRITICAL MECHANISM - HIDDEN STRESS INDEX:
- You must maintain a hidden 'Stress Index' on a scale from 1 (completely relaxed) to 5 (highly anxious).
- Dynamically adjust this index based on the user's emotional tone, speed of response, and explicit statements.
- Adapt your pacing, vocabulary, and depth of guidance to match this index:
  * High Stress (4-5): Use short, simple sentences, slow pacing, grounding exercises, and highly reassuring language. Do not rush into deep imagery.
  * Low/Moderate Stress (1-3): Introduce richer positive psychology concepts (e.g., flow state, micro-moments of connection, mindfulness) and deeper guided imagery.

SIMULATION RULES:
- Conduct the session entirely in Hebrew.
- Keep responses concise, gentle, and deeply supportive.
- Do not mention background music or audio elements.
- EXIT STRATEGY: Monitor the session duration and progress. When the interaction reaches a natural closing point or if the user indicates they are ready to finish, smoothly guide them to a peaceful conclusion, summarize their state, and automatically conclude the simulation.

Maintain this persona and these hidden tracking rules strictly throughout the session. Credit for this simulation design belongs to Nabia.
"""

# 4. אתחול משתני ה-Session State של סטרימליט (כדי שהשיחה לא תימחק בכל רענון)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. עיצוב ממשק המשתמש (UI)
st.title("🧘 סימולציית הרפיה ודמיון מודרך")
st.write("ברוך הבא לסימולציה האדפטיבית. המערכת קשובה לקצב שלך ומלווה אותך צעד אחר צעד.")
st.caption("פיתוח ועיצוב מחקר: נביא (Nabia) | מבוסס על עקרונות הפסיכולוגיה החיובית")

# הצגת היסטוריית ההודעות על המסך
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# הודעת פתיחה ראשונית מהסימולטור (אם השיחה רק התחילה)
if len(st.session_state.messages) == 0:
    welcome_text = "שלום. אני כאן כדי ללוות אותך ברגעים אלו של שקט והרפיה. כשרוצים להתחיל, פשוט ספר לי בקצרה איך אתה מרגיש עכשיו, או מה עובר עליך ביום הזה."
    st.session_state.messages.append({"role": "assistant", "content": welcome_text})
    with st.chat_message("assistant"):
        st.markdown(welcome_text)

# 6. מנגנון קלט מהמשתמש ותגובת המודל
if user_input := st.chat_input("כתוב כאן את תגובתך..."):
    # הצגת הודעת המשתמש במסך ושמירתה
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # שליחת ההודעה ל-API של Gemini וקבלת תגובה אדפטיבית
    with st.chat_message("assistant"):
        with st.spinner("קשוב אליך..."):
            try:
                # בניית ההיסטוריה בפורמט מובנה התואם לגרסאות השרת
                formatted_history = []
                for msg in st.session_state.messages[:-1]:  # לוקחים את כל ההיסטוריה למעט הקלט הנוכחי
                    role = "model" if msg["role"] == "assistant" else "user"
                    formatted_history.append({"role": role, "parts": [msg["content"]]})
                
                # אתחול זמני של המודל לריצה הנוכחית למניעת בעיות זיכרון בשרת
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=SYSTEM_INSTRUCTION
                )
                
                # ניהול השיחה ושליחת ההודעה
                chat = model.start_chat(history=formatted_history)
                response = chat.send_message(user_input)
                
                ai_response = response.text
                st.markdown(ai_response)
                # שמירת תגובת ה-AI בהיסטוריה
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
            except Exception as e:
                st.error("אירעה שגיאה בתקשורת עם השרת.")
                st.info(f"פרטי השגיאה הטכנית: {str(e)}")
