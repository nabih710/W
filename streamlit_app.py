import streamlit as st
from google import genai
from google.genai import types

# 1. הגדרת תצורת הדף
st.set_page_config(page_title="סימולציית הרפיה אדפטיבית", layout="centered", initial_sidebar_state="collapsed")

# 2. שליפת מפתח ה-API ואתחול הלקוח החדש של גוגל
# 2. שליפת מפתח ה-API ואתחול הלקוח החדש של גוגל
if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
    # שימוש ב-ClientOptions כדי להגדיר במפורש את ערוץ ה-API עבור מפתחות AQ החדשים
    from google.genai import client_options
    opts = client_options.ClientOptions(api_key=st.secrets["GEMINI_API_KEY"])
    client = genai.Client(options=opts)
else:
    st.error("מפתח ה-API חסר. אנא הגדר את GEMINI_API_KEY ב-Secrets של Streamlit.")
    st.stop()
# 3. הגדרת הנחיות המערכת (System Instruction)
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

# 4. אתחול משתני ה-Session State
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

# הודעת פתיחה ראשונית
if len(st.session_state.messages) == 0:
    welcome_text = "שלום. אני כאן כדי ללוות אותך ברגעים אלו של שקט והרפיה. כשרוצים להתחיל, פשוט ספר לי בקצרה איך אתה מרגיש עכשיו, או מה עובר עליך ביום הזה."
    st.session_state.messages.append({"role": "assistant", "content": welcome_text})
    with st.chat_message("assistant"):
        st.markdown(welcome_text)

# 6. מנגנון קלט מהמשתמש ותגובת המודל
if user_input := st.chat_input("כתוב כאן את תגובתך..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("assistant"):
        with st.spinner("קשוב אליך..."):
            try:
                # בניית היסטוריית השיחה בפורמט החדש של ה-SDK
                contents = []
                for msg in st.session_state.messages:
                    role = "model" if msg["role"] == "assistant" else "user"
                    contents.append(
                        types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
                    )
                
                # קריאה למודל העדכני באמצעות ה-Client החדש
                response = client.models.generate_content(
                    model='gemini-1.5-flash-latest',
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION
                    )
                )
                
                ai_response = response.text
                st.markdown(ai_response)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
            except Exception as e:
                st.error("אירעה שגיאה בתקשורת עם השרת החדש.")
                st.info(f"פרטי השגיאה הטכנית: {str(e)}")
