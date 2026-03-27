import streamlit as st
from streamlit_gsheets import GSheetsConnection
from gtts import gTTS
import pandas as pd
import base64
import io
import random
from datetime import datetime

# --- 1. ตั้งค่าหน้าจอและสไตล์ ---
st.set_page_config(page_title="CEFR Vocab Hero Pro", page_icon="🏆", layout="wide")

# --- 2. การเชื่อมต่อ Google Sheets (ใส่ URL ของคุณที่นี่) ---
# หมายเหตุ: หากยังไม่มี URL ให้ใช้ไฟล์ vocab.csv ที่อัปโหลดขึ้น GitHub แทนได้
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/your-id-here/edit#gid=0"

# --- 3. เริ่มต้น Session State (เก็บข้อมูลชั่วคราวขณะเล่น) ---
if 'score' not in st.session_state: st.session_state.score = 0
if 'streak' not in st.session_state: st.session_state.streak = 0
if 'total_played' not in st.session_state: st.session_state.total_played = 0
if 'wrong_words' not in st.session_state: st.session_state.wrong_words = set()

# --- 4. ฟังก์ชันระบบเสียง ---
def speak(text):
    try:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(md, unsafe_allow_html=True)
    except: pass

# --- 5. ฟังก์ชันโหลดข้อมูล ---
@st.cache_data(ttl=600)
def load_data():
    try:
        # พยายามโหลดจาก Google Sheets ก่อน
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn.read(spreadsheet=GOOGLE_SHEET_URL)
    except:
        # ถ้าโหลดไม่ได้ ให้โหลดจากไฟล์ vocab.csv ใน GitHub แทน
        return pd.read_csv("vocab.csv")

# โหลดข้อมูลคำศัพท์
try:
    df = load_data()
except:
    st.error("ไม่พบไฟล์ข้อมูล กรุณาอัปโหลด vocab.csv ขึ้น GitHub")
    st.stop()

# --- 6. Sidebar Menu ---
with st.sidebar:
    st.title("🚀 Vocab Hero")
    mode = st.radio("เมนูหลัก:", ["📖 เรียนรู้คำศัพท์", "🧠 ทำแบบทดสอบ", "📊 สถิติ & ใบเซอร์"])
    st.divider()
    st.metric("Score", f"{st.session_state.score}/{st.session_state.total_played}")
    st.metric("Current Streak", f"🔥 {st.session_state.streak}")
    if st.button("Reset Stats"):
        st.session_state.score = 0
        st.session_state.streak = 0
        st.session_state.total_played = 0
        st.session_state.wrong_words = set()
        st.rerun()

# --- 7. โหมดเรียนรู้ ---
if mode == "📖 เรียนรู้คำศัพท์":
    st.header("📖 Learning Center")
    level = st.selectbox("ระดับ CEFR", ["All"] + sorted(df['level'].unique().tolist()))
    f_df = df if level == "All" else df[df['level'] == level]
    
    word_choice = st.selectbox("เลือกคำศัพท์", f_df['word'])
    w = f_df[f_df['word'] == word_choice].iloc[0]
    
    with st.container(border=True):
        c1, c2 = st.columns([4, 1])
        c1.subheader(f"{w['word']} ({w['level']}) - {w['pos']}")
        if c2.button("🔊 ฟังเสียง"): speak(w['word'])
        
        t1, t2, t3 = st.tabs(["ความหมาย", "Synonyms/Antonyms", "ตัวอย่าง"])
        with t1:
            st.write(f"🇹🇭 {w['def_th']}")
            st.write(f"🇺🇸 {w['def_en']}")
                with t2:
            # ส่วนของ Synonyms
            col_s1, col_s2 = st.columns([4, 1])
            col_s1.write(f"✅ Synonyms: {w['synonyms']}")
            if col_s2.button("🔊", key="syn_btn"): 
                speak(w['synonyms'])
            
            st.divider() # ขีดเส้นคั่นเล็กน้อยให้ดูง่าย
            
            # ส่วนของ Antonyms
            col_a1, col_a2 = st.columns([4, 1])
            col_a1.write(f"❌ Antonyms: {w['antonyms']}")
            if col_a2.button("🔊", key="ant_btn"): 
                speak(w['antonyms'])
        with t3:
            st.info(w['example'])
            if st.button("🔊 อ่านตัวอย่าง"): speak(w['example'])

# --- 8. โหมดทำแบบทดสอบ ---
elif mode == "🧠 ทำแบบทดสอบ":
    st.header("🧠 Quiz Challenge")
    if len(df) < 4:
        st.error("ต้องการคำศัพท์อย่างน้อย 4 คำเพื่อทำ Quiz")
    else:
        if 'q_data' not in st.session_state:
            q_row = df.sample(1).iloc[0]
            correct = q_row['def_th']
            others = df[df['def_th'] != correct]['def_th'].sample(3).tolist()
            opts = others + [correct]
            random.shuffle(opts)
            st.session_state.q_data = {'word': q_row['word'], 'ans': correct, 'opts': opts}

        qd = st.session_state.q_data
        st.subheader(f"คำว่า '{qd['word']}' แปลว่าอะไร?")
        ans = st.radio("ตัวเลือก:", qd['opts'])
        
        if st.button("ส่งคำตอบ"):
            st.session_state.total_played += 1
            if ans == qd['ans']:
                st.success("ถูกต้อง! 🎉")
                st.session_state.score += 1
                st.session_state.streak += 1
                if qd['word'] in st.session_state.wrong_words:
                    st.session_state.wrong_words.remove(qd['word'])
            else:
                st.error(f"ผิดครับ! คำตอบคือ: {qd['ans']}")
                st.session_state.streak = 0
                st.session_state.wrong_words.add(qd['word'])
            
            if st.button("ข้อถัดไป ➡️"):
                del st.session_state.q_data
                st.rerun()

# --- 9. โหมดสถิติและใบเซอร์ ---
elif mode == "📊 สถิติ & ใบเซอร์":
    st.header("🏆 ความสำเร็จของคุณ")
    if st.session_state.streak >= 10:
        st.balloons()
        st.markdown("""
        <div style="text-align:center; padding:30px; border: 10px solid gold; border-radius: 15px;">
            <h1 style="color:gold;">📜 CERTIFICATE</h1>
            <h2>Congratulations!</h2>
            <p>You've achieved a 10-answer streak!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"ทำ Streak ให้ครบ 10 เพื่อรับใบเซอร์ (ตอนนี้: {st.session_state.streak})")
    
    st.divider()
    st.subheader("❌ คำศัพท์ที่ตอบผิด (ควรทบทวน)")
    if st.session_state.wrong_words:
        for ww in st.session_state.wrong_words:
            st.write(f"- {ww}")
    else:
        st.write("ยังไม่มีคำที่ตอบผิด")
