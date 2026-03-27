import streamlit as st
import pandas as pd
from gtts import gTTS
import base64
import io
import random

# --- 1. การตั้งค่าหน้าจอ ---
st.set_page_config(page_title="CEFR Vocab Hero", page_icon="🎓", layout="wide")

# --- 2. ฟังก์ชันเล่นเสียง ---
def speak(text):
    if text and text != "-":
        try:
            tts = gTTS(text=text, lang='en')
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)
        except:
            pass

# --- 3. โหลดข้อมูล ---
@st.cache_data
def load_data():
    try:
        # ดึงข้อมูลจากไฟล์ vocab.csv ใน GitHub
        return pd.read_csv("vocab.csv")
    except:
        # ข้อมูลสำรองเผื่อไฟล์มีปัญหา
        return pd.DataFrame([{
            "word": "Believe", "level": "A2", "pos": "V", 
            "def_th": "เชื่อ", "def_en": "To think that something is true",
            "synonyms": "Trust", "antonyms": "Doubt", 
            "example": "I believe you.", "example_th": "ฉันเชื่อคุณ"
        }])

df = load_data()

# --- 4. สถานะแอป (Session State) ---
if 'score' not in st.session_state: st.session_state.score = 0
if 'total' not in st.session_state: st.session_state.total = 0

# --- 5. เมนู Sidebar ---
with st.sidebar:
    st.title("🎯 Vocab Hero")
    menu = st.radio("เลือกโหมด:", ["📖 เรียนรู้", "🧠 ทดสอบ"])
    st.divider()
    st.metric("คะแนน", f"{st.session_state.score}/{st.session_state.total}")

# --- 6. โหมดเรียนรู้ ---
if menu == "📖 เรียนรู้":
    st.header("📖 Learning Center")
    
    # เลือกคำศัพท์
    col_a, col_b = st.columns([1, 2])
    with col_a:
        level_choice = st.selectbox("ระดับ CEFR:", sorted(df['level'].unique().tolist()))
        f_df = df[df['level'] == level_choice]
        word_choice = st.selectbox("เลือกคำศัพท์:", f_df['word'])
    
    # แสดงรายละเอียด
    with col_b:
        w = f_df[f_df['word'] == word_choice].iloc[0]
        with st.container(border=True):
            # หัวข้อคำศัพท์ + ปุ่มเสียง
            c1, c2 = st.columns([4, 1])
            c1.subheader(f"{w['word']} ({w['level']}) - {w['pos']}")
            if c2.button("🔊 ฟัง", key="main_v"): speak(w['word'])
            
            # แบ่ง Tab ข้อมูล
            t1, t2, t3 = st.tabs(["ความหมาย", "Synonyms/Antonyms", "ตัวอย่างประโยค"])
            
            with t1:
                st.write(f"🇹🇭 {w['def_th']}")
                st.write(f"🇺🇸 {w['def_en']}")
            
            with t2:
                # ส่วน Synonyms
                s_c1, s_c2 = st.columns([4, 1])
                s_c1.write(f"✅ Synonyms: {w['synonyms']}")
                if s_c2.button("🔊", key="s_v"): speak(w['synonyms'])
                st.divider()
                # ส่วน Antonyms
                a_c1, a_c2 = st.columns([4, 1])
                a_c1.write(f"❌ Antonyms: {w['antonyms']}")
                if a_c2.button("🔊", key="a_v"): speak(w['antonyms'])
                
            with t3:
                # แสดงประโยคตัวอย่างอังกฤษและไทย
                st.info(f"🇬🇧 {w['example']}")
                # ตรวจสอบว่ามีคอลัมน์ example_th หรือไม่
                if 'example_th' in w and pd.notna(w['example_th']):
                    st.success(f"🇹🇭 {w['example_th']}")
                
                if st.button("🔊 อ่านประโยคภาษาอังกฤษ", key="ex_v"): 
                    speak(w['example'])

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

    if st.button("ส่งคำตอบ"):
        st.session_state.total += 1
        if user_ans == q['ans']:
            st.success("ถูกต้อง! 🎉")
            st.session_state.score += 1
        else:
            st.error(f"ผิดครับ คำตอบคือ: {q['ans']}")
        
        if st.button("ข้อถัดไป ➡️"):
            del st.session_state.quiz_q
            st.rerun()
def load_data():
    try:
        # ดึงข้อมูลจากไฟล์ vocab.csv ที่อยู่ใน GitHub ของคุณ
        return pd.read_csv("vocab.csv")
    except:
        return pd.DataFrame([{"word": "Example", "level": "A1", "pos": "N", "def_th": "ตัวอย่าง", "def_en": "Example", "synonyms": "Sample", "antonyms": "-", "example": "This is an example."}])

df = load_data()

# --- 4. จัดการสถานะการเล่น (Session State) ---
if 'score' not in st.session_state: st.session_state.score = 0
if 'total' not in st.session_state: st.session_state.total = 0
if 'streak' not in st.session_state: st.session_state.streak = 0

# --- 5. เมนู Sidebar ---
with st.sidebar:
    st.title("🎯 Vocab Hero")
    menu = st.radio("เลือกโหมด:", ["📖 เรียนรู้", "🧠 ทดสอบ", "🏆 ความสำเร็จ"])
    st.divider()
    st.metric("คะแนนสะสม", f"{st.session_state.score}/{st.session_state.total}")
    st.metric("Streak ปัจจุบัน", f"🔥 {st.session_state.streak}")
    if st.button("ล้างสถิติ"):
        st.session_state.score = 0
        st.session_state.total = 0
        st.session_state.streak = 0
        st.rerun()

# --- 6. โหมดเรียนรู้ ---
if menu == "📖 เรียนรู้":
    st.header("📖 Learning Center")
    
    col_a, col_b = st.columns([1, 2])
    with col_a:
        level_choice = st.selectbox("ระดับ CEFR:", ["All"] + sorted(df['level'].unique().tolist()))
        filtered_df = df if level_choice == "All" else df[df['level'] == level_choice]
        word_choice = st.selectbox("เลือกคำศัพท์:", filtered_df['word'])
    
    with col_b:
        w = filtered_df[filtered_df['word'] == word_choice].iloc[0]
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.subheader(f"{w['word']} ({w['level']})")
            c1.caption(f"Part of Speech: {w['pos']}")
            if c2.button("🔊 ฟัง", key="main_v"): speak(w['word'])
            
            t1, t2, t3 = st.tabs(["ความหมาย", "Synonyms/Antonyms", "ตัวอย่างประโยค"])
            
            with t1:
                st.write(f"🇹🇭 {w['def_th']}")
                st.write(f"🇺🇸 {w['def_en']}")
            
            with t2:
                # ส่วน Synonyms
                s_c1, s_c2 = st.columns([4, 1])
                s_c1.write(f"✅ Synonyms: {w['synonyms']}")
                if s_c2.button("🔊", key="s_v"): speak(w['synonyms'])
                st.divider()
                # ส่วน Antonyms
                a_c1, a_c2 = st.columns([4, 1])
                a_c1.write(f"❌ Antonyms: {w['antonyms']}")
                if a_c2.button("🔊", key="a_v"): speak(w['antonyms'])
                
            with t3:
                st.info(w['example'])
                if st.button("🔊 อ่านประโยคตัวอย่าง", key="ex_v"): speak(w['example'])

# --- 7. โหมดทดสอบ ---
elif menu == "🧠 ทดสอบ":
    st.header("🧠 Quick Quiz")
    
    if 'quiz_q' not in st.session_state:
        q_row = df.sample(1).iloc[0]
        correct = q_row['def_th']
        distractors = df[df['def_th'] != correct]['def_th'].sample(3).tolist()
        options = distractors + [correct]
        random.shuffle(options)
        st.session_state.quiz_q = {'word': q_row['word'], 'ans': correct, 'opts': options}

    q = st.session_state.quiz_q
    st.subheader(f"คำว่า '{q['word']}' แปลว่าอะไร?")
    user_ans = st.radio("เลือกคำตอบที่ถูกต้อง:", q['opts'])

    if st.button("ส่งคำตอบ"):
        st.session_state.total += 1
        if user_ans == q['ans']:
            st.success("ถูกต้องยอดเยี่ยม! 🎉")
            st.session_state.score += 1
            st.session_state.streak += 1
        else:
            st.error(f"ผิดนิดเดียว! คำตอบคือ: {q['ans']}")
            st.session_state.streak = 0
        
        if st.button("ข้อถัดไป ➡️"):
            del st.session_state.quiz_q
            st.rerun()

# --- 8. โหมดความสำเร็จ ---
elif menu == "🏆 ความสำเร็จ":
    st.header("🏆 Achievement Board")
    if st.session_state.streak >= 5:
        st.balloons()
        st.success("คุณได้รับเหรียญตรา: นักเรียนดีเด่น! 🎖️")
        st.markdown(f"""
        <div style="border: 5px solid gold; padding: 20px; text-align: center; border-radius: 15px;">
            <h1 style="color: gold;">CERTIFICATE OF EXCELLENCE</h1>
            <p>ขอชื่นชมที่คุณทำ Streak ได้ถึง {st.session_state.streak} ข้อ!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("ทำ Streak ให้ครบ 5 ข้อเพื่อปลดล็อกใบประกาศ!")
