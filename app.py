import streamlit as st
import requests
import uuid

# --- 1. ページ設定 ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="⚖️", layout="centered")

# --- 2. デザインを磨き上げるカスタムCSS ---
st.markdown("""
    <style>
    /* 全体の背景 */
    .stApp {
        background-color: #f4f7f9;
    }
    
    /* ヘッダーエリア */
    .header-box {
        background: linear-gradient(135deg, #061e3d 0%, #10305a 100%);
        padding: 40px 20px;
        border-radius: 0px 0px 20px 20px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        border-bottom: 5px solid #c5a059; /* ゴールドのライン */
        margin: -6rem -2rem 2rem -2rem;
    }
    
    /* ロゴの再現 (H IMAI イメージ) */
    .logo-circle {
        width: 80px;
        height: 80px;
        background: white;
        border: 3px solid #061e3d;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 15px;
        position: relative;
    }
    .logo-h {
        color: #061e3d;
        font-size: 38px;
        font-weight: 900;
        font-family: 'Georgia', serif;
    }
    .logo-imai {
        position: absolute;
        bottom: 12px;
        font-size: 10px;
        font-weight: bold;
        color: #061e3d;
        letter-spacing: 1px;
    }

    .header-title {
        font-size: 26px;
        font-weight: 700;
        margin: 10px 0 5px 0;
        letter-spacing: 1px;
    }
    
    .header-subtitle {
        font-size: 14px;
        opacity: 0.9;
        font-weight: 300;
    }

    /* フッター（コピーライト） */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #061e3d;
        color: white;
        text-align: center;
        padding: 10px 0;
        font-size: 12px;
        z-index: 100;
    }

    /* チャット入力欄をフッターより上に配置するための余白 */
    .main {
        margin-bottom: 60px;
    }
    </style>
    
    <div class="header-box">
        <div class="logo-circle">
            <span class="logo-h">H</span>
            <span class="logo-imai">IMAI</span>
        </div>
        <div class="header-title">今井社会保険労務士事務所</div>
        <div class="header-subtitle">就業規則・労務リスク判定 AIアシスタント</div>
    </div>
    
    <div class="footer">
        © 2024 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office
    </div>
    """, unsafe_allow_html=True)

# --- 3. Dify API 設定 ---
DIFY_API_KEY = st.secrets.get("DIFY_API_KEY", "YOUR_API_KEY_HERE")
DIFY_ENDPOINT = "https://api.dify.ai/v1/chat-messages"

if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

# 履歴表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. メイン処理 ---
if prompt := st.chat_input("就業規則の条文を入力してください..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("⚖️ 判定中...")
        
        try:
            response = requests.post(
                DIFY_ENDPOINT,
                headers={"Authorization": f"Bearer {DIFY_API_KEY}", "Content-Type": "application/json"},
                json={
                    "inputs": {},
                    "query": prompt,
                    "response_mode": "blocking",
                    "user": st.session_state.user_id,
                    "conversation_id": ""
                }
            )
            response.raise_for_status()
            answer = response.json().get("answer", "回答が取得できませんでした。")
            
            placeholder.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")