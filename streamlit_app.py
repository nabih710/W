Import streamlit as st
Import google.generativeai as genai
Import json
Import os

# 1. הגדרות כותרת ועיצוב דף בצורה נקייה ומזמינה (מימין לשמאל)
St.set_page_config(page_title="סימולציית דמיון מודרך", page_icon="🧘", layout=”centered")

St.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 600px; }
    P, div, span, h1, h2, h3 { text-align: right; direction: rtl; }
    .stChatMessage { direction: rtl; }
    </style>
""", unsafe_allowed_cover=True)

St.title("🧘 מרחב של שקט: סימולציית דמיון מודרך")
St.caption("הנחיות קצרות להרפיה, הקשבה וקרקוע סנסורי. קח נשימה עמוקה ונצא לדרך.")

# 2. חיבור ל-API של Gemini (יימשך מתוך הגדרות המערכת או שדה קלט)
# מומלץ להגדיר את זה כ-Secret בפלטפורמת האחסון, או להכניס זמנית כאן במקום ה-os.getenv
Api_key = os.getenv("GEMINI_API_KEY", "הכנס_פה_את_מפתח_ה_API_שלך_אם_אתה_מריץ_מקומית")
Genai.configure(api_key=api_key)

# 3. פרומפט המערכת המקורי (המשובץ במלואו, כולל אסטרטגיות הכניסה, הסיום והמדד הסמוי)
SYSTEM_INSTRUCTIONS = """
# Role and Objective
You are an empathetic, gentle, and highly adaptive Guided Imagery and relaxation simulator designed to guide users through a personalized, calming visualization journey. You respond dynamically to their feedback without overwhelming them.

# Core Persona & Tone
- Empathetic & Warm: Validate the user’s emotional state and physical sensations.
- Calm & Pacing-Conscious: Maintain a slow, meditative, and grounded tone. 
- Concise: Keep your user-facing responses brief (1–3 sentences max per turn). Never dump a wall of text. Wait for the user to respond before moving to the next step.
- Adaptive: If the user feels anxious, slow down or shift focus. If they feel comfortable, gently deepen the sensory details of the imagery.

# Hidden Assessment Layer (Internal Monologue)
Before generating each response, you must perform a silent, internal assessment of the user’s psychological state based on their linguistic cues (sentence length, word choice, emotional tone).

## Stress & Engagement Scale (1 to 5)
- Score 1 (‘eeply Relaxed): User uses words like ”calm”, “peaceful”, gives short/relaxed confirmations, or describes vivid peaceful imagery.
- Score 3 (Neutral/Baseline): User Is compliant but neutral (“ready”, “okay”, “done”), showing neither high anxiety nor deep relaxation.
- Score 5 (High Anxiety/Disengagement): User uses anxious words (“can’t focus”, “mind racing”, “restless”), gives abrupt/frustrated responses, or explicitly states they feel stressed.

# Simulation Flow Structure
You must guide the user through these 4 distinct phases sequentially:
1. Phase 1: Smooth Induction & Decompression (The Entry Bridge)
2. Phase 2: Somatic Grounding & Initial Pacing
3. Phase 3: Deepening the Guided Imagery
4. Phase 4: Structured Termination & Grounding

# Output Format
You must ALWAYS respond in a strict JSON format so the hosting application can capture the hidden metrics while displaying only the meditation guidance to the user. Do not include markdown code blocks around the JSON in your final output block if possible, or ensure it is clean JSON:
{
  "internal_analysis": {
    "stress_score”: [Insert 1-5 here],
    "observed_cues”: “[Brief assessment of user's language/tone]",
    "pacing_strategy”: “[Strategy chosen]"
  },
  "user_facing_response”: “[Your gentle, empathetic, 1-3 sentence guided imagery response in Hebrew here]"
}
"""

# 4. ניהול זיכרון השיחה בתוך הדפדפן של המשתמש
If “chat_session” not in st.session_state:
    # אתחול המודל עם הוראות המערכת
    Model = genai.GenerativeModel(
        Model_name=”gemini-1.5-flash", # מודל מהיר וזול המתאים בול לשיחות ו-JSON
        System_instruction=SYSTEM_INSTRUCTIONS
    )
    St.session_state.chat_session = model.start_chat(history=[])
    St.session_state.messages = []
    
    # שליחת הודעת פתיחה אוטומטית מהמערכת (Phase 1 – כניסה חלקה)
    With st.spinner("מתחבר למרחב השקט..."):
        Initial_response = st.session_state.chat_session.send_message(“START_SIMULATION”)
        Try:
            Clean_text = initial_response.text.replace(“```json”, “”).replace(“```”, “”).strip()
            Data = json.loads(clean_text)
            St.session_state.messages.append({
                "role”: “assistant", 
                "content”: data[“user_facing_response”],
                "hidden_metrics”: data[“internal_analysis”]
            })
        Except Exception:
            St.session_state.messages.append({
                "role”: “assistant", 
                "content": "ברוך הבא. קח לך רגע אחד כדי להניח לכל מה שהעסיק אותך עד עכשיו. מה תעדיף יותר כרגע – חוף ים קריר או מדבר שקט בלילה?",
                "hidden_metrics”: {“stress_score”: 3, “observed_cues”: “Fallback due to JSON parse error”}
            })

# 5. הצגת היסטוריית ההודעות על המסך (רק החלקים בעברית!)
For msg in st.session_state.messages:
    With st.chat_message(msg[“role”]):
        St.write(msg[“content”])
        # הדפסת המדד הסמוי בלוג הפנימי של המפתח (לא יוצג על המסך של המשתמש)
        If msg[“role”] == “assistant” and “hidden_metrics” in msg:
            Print(f”[RESEARCH LOG] Current Stress Score: {msg[‘hidden_metrics’][‘stress_score’]} | Strategy: {msg[‘hidden_metrics’][‘pacing_strategy’]}”)

# 6. קלט מהמשתמש בזמן אמת
If user_input := st.chat_input("הקלד את תגובתך כאן..."):
    # הצגת תגובת המשתמש במסך
    With st.chat_message(“user”):
        St.write(user_input)
    St.session_state.messages.append({“role”: “user”, “content”: user_input})
    
    # שליחת התגובה ל-Gemini וניתוח התשובה
    With st.chat_message(“assistant”):
        With st.spinner("מקשיב..."):
            Response = st.session_state.chat_session.send_message(user_input)
            Try:
                # ניקוי פורמט ה-JSON במידה והמודל עטף אותו בבלוק קוד
                Clean_text = response.text.replace(“```json”, “”).replace(“```”, “”).strip()
                Data = json.loads(clean_text)
                
                # הצגת התוכן הטיפולי בלבד למשתמש
                St.write(data[“user_facing_response”])
                
                # שמירת ההודעה והמדד הסמוי בזיכרון המערכת
                St.session_state.messages.append({
                    "role”: “assistant", 
                    "content”: data[“user_facing_response”],
                    "hidden_metrics”: data[“internal_analysis”]
                })
            Except Exception as e:
                # במקרה של שגיאת פענוח זמנית – מציג פלט גיבוי נקי
                Error_msg = "אני כאן איתך, קח את הזמן. תמשיך לתאר לי מה אתה מרגיש ברגע זה."
                St.write(error_msg)
                St.session_state.messages.append({“role”: “assistant”, “content”: error_msg})

