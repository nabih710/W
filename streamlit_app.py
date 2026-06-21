import streamlit as st
from google import genai

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
    # אתחול נקי של ה-Client
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("מפתח ה-API חסר. אנא הגדר את GEMINI_API_KEY ב-Secrets של Streamlit.")
    st.stop()

# 3. ניהול זיכרון השיחה והגדרת הודעת הפתיחה האסטרטגית קבועה מראש
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "שלום וברוך הבא לסימולציית ההנחיה האינטראקטיבית. כאן נתרגל ונסמלץ מצבי הנחיה מותאמים אישית. כדי שנוכל להתחיל, נשמח לשמוע: מהו מדד הלחץ הנוכחי שלך, ואיזה סוג של דימוי או סביבה טבעית היית רוצה לחקור היום?"
        }
    ]

# הצגת היסטוריית ההודעות (הודעת הפתיחה תופיע מיד)
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
            # בניית מבנה ההיסטוריה בפורמט מילוני פשוט, התואם לשרת החדש
            contents = []
            for msg in st.session_state.messages:
                role = "model" if msg["role"] == "assistant" else "user"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })

            # קריאה למודל באמצעות מבנה מילוני ישיר (עוקף את באג ה-OAuth)
            response = client.models.generate_content(
                model='models/gemini-1.5-flash',

                contents=contents,
                config={'system_instruction': SYSTEM_INSTRUCTION}
            )
            
            ai_response = response.text
            message_placeholder.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except Exception as e:
            message_placeholder.error("אירעה שגיאה במהלך הסימולציה. אנא ודא שמפתח ה-API תקין.")
            st.write(f"פרטי השגיאה הטכנית: {e}")

