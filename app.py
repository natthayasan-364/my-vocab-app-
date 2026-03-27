import streamlit as st
import pandas as pd
from gtts import gTTS
import base64
import io
import random

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CEFR Vocab Hero Pro", page_icon="🎓", layout="wide")

# --- 2. ฟังก์ชันเล่นเสียง ---
def speak(text, unique_key):
    if text and text != "-":
        try:
            tts = gTTS(text=text, lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            md = f'<audio autoplay="true" key="{unique_key}"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)
        except:
            pass

# --- 3. โหลดข้อมูล ---
@st.cache_data
def load_data():
    try:
        return pd.read_csv("vocab.csv")
    except:
        # ข้อมูลตัวอย่างหากโหลดไฟล์ไม่ได้
        return pd.DataFrame([{
            "word": "Believe", "level": "A2", "pos": "V", 
            "def_th": "เชื่อ", "def_en": "To think that something is true",
            "synonyms": "Trust", "synonyms_th": "ไว้ใจ",
            "antonyms": "Doubt", "antonyms_th": "สงสัย",
            "example": "I believe you.", "example_th": "ฉันเชื่อคุณ"
        }])

df = load_data()

# --- 4. สถานะแอป ---
if 'score' not in st.session_state: st.session_state.score = 0
if 'total' not in st.session_state: st.session_state.total = 0

# --- 5. เมนู Sidebar ---
with st.sidebar:
    st.title("🎯 Vocab Hero")
    menu = st.radio("เลือกโหมด:", ["📖 เรียนรู้", "🧠 ทดสอบ"])
    st.divider()
    st.metric("คะแนนของคุณ", f"{st.session_state.score}/{st.session_state.total}")

# --- 6. โหมดเรียนรู้ ---
if menu == "📖 เรียนรู้":
    st.header("📖 Learning Center")
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        level_list = sorted(df['level'].unique().tolist())
        level_choice = st.selectbox("ระดับ CEFR:", level_list)
        f_df = df[df['level'] == level_choice]
        word_choice = st.selectbox("เลือกคำศัพท์:", f_df['word'])
    
    with col_b:
        w = f_df[f_df['word'] == word_choice].iloc[0]
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.subheader(f"{w['word']} ({w['level']}) - {w['pos']}")
            if c2.button("🔊 ฟัง", key="btn_main_word"): 
                speak(w['word'], "audio_main")
            
            t1, t2, t3 = st.tabs(["ความหมาย", "Synonyms/Antonyms", "ตัวอย่างประโยค"])
            
            with t1:
                st.write(f"🇹🇭 {w['def_th']}")
                st.write(f"🇺🇸 {w['def_en']}")
            
            with t2:
                # Synonyms
                s1, s2 = st.columns([4, 1])
                s_text = f"✅ Synonyms: **{w['synonyms']}**"
                if 'synonyms_th' in w and pd.notna(w['synonyms_th']):
                    s_text += f" ({w['synonyms_th']})"
                s1.write(s_text)
                if s2.button("🔊", key="btn_syn"): 
                    speak(w['synonyms'], "audio_syn")
                
                st.divider()
                
                # Antonyms
                a1, a2 = st.columns([4, 1])
                a_text = f"❌ Antonyms: **{w['antonyms']}**"
                if 'antonyms_th' in w and pd.notna(w['antonyms_th']):
                    a_text += f" ({w['antonyms_th']})"
                a1.write(a_text)
                if a2.button("🔊", key="btn_ant"): 
                    speak(w['antonyms'], "audio_ant")
                
            with t3:
                st.info(f"🇬🇧 {w['example']}")
                if 'example_th' in w and pd.notna(w['example_th']):
                    st.success(f"🇹🇭 {w['example_th']}")
                if st.button("🔊 อ่านตัวอย่าง", key="btn_ex"): 
                    speak(w['example'], "audio_ex")

# --- 7. โหมดทดสอบ ---
elif menu == "🧠 ทดสอบ":
    st.header("🧠 Quick Quiz")
    if 'quiz_q' not in st.session_state:
        q_row = df.sample(1).iloc[0]
        correct = q_row['def_th']
        distractors = df[df['def_th'] != correct]['def_th'].sample(min(3, len(df)-1)).tolist()
        options = distractors + [correct]
        random.shuffle(options)
        st.session_state.quiz_q = {'word': q_row['word'], 'ans': correct, 'opts': options}

    q = st.session_state.quiz_q
    st.subheader(f"คำว่า '{q['word']}' แปลว่าอะไร?")
    user_ans = st.radio("เลือกคำตอบ:", q['opts'])

    if st.button("ส่งคำตอบ", key="btn_submit_quiz"):
        st.session_state.total += 1
        if user_ans == q['ans']:
            st.success("ถูกต้อง! 🎉")
            st.session_state.score += 1
        else:
            st.error(f"ผิดครับ คำตอบคือ: {q['ans']}")
        
        if st.button("ข้อถัดไป ➡️", key="btn_next_quiz"):
            del st.session_state.quiz_q
            st.rerun()
