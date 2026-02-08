import streamlit as st
import requests
import uuid

# --- 1. ページ設定 ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="⚖️", layout="centered")

# --- 2. 白ベース・見切れ防止カスタムCSS ---
st.markdown("""
    <style>
    /* 全体の背景を白に */
    .stApp {
        background-color: #ffffff;
    }
    
    /* ヘッダーエリア：見切れ防止のためトップに余白を確保 */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        padding: 60px 20px 20px 0; /* 上部の余白を60pxに拡大 */
        border-bottom: 2px solid #f0f2f6;
        margin-bottom: 30px;
        background-color: #ffffff;
    }
    
    /* ロゴの再現 */
    .logo-circle {
        width: 60px;
        height: 60px;
        background: #061e3d;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-right: 20px;
        flex-shrink: 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .logo-h {
        color: #ffffff;
        font-size: 28px;
        font-weight: 900;
        font-family: 'Georgia', serif;
        line-height: 1;
    }
    .logo-imai {
        font-size: 8px;
        font-weight: bold;
        color: #ffffff;
        letter-spacing: 1px;
        margin-top: -2px;
    }

    /* タイトルテキスト */
    .title-text-box {
        display: flex;
        flex-direction: column;
    }
    .header-title {
        color: #061e3d;
        font-size: 22px;
        font-weight: 700;
        margin: 0;
    }
    .header-subtitle {
        color: #666666;
        font-size: 13px;
        margin-top: 4px;
    }

    /* フッター（画面最下部に固定） */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #061e3d;
        color: white;
        text-align: center;
        padding: 10px 0;
        font-size: 11px;
        z-index: 100;
    }

    /* Streamlit標準のヘッダー（黒い帯）を非表示にする場合は以下 */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* コンテンツの余白調整 */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 6rem !important;
    }
    </style>
    
    <div class="header-container">
        <div class="logo-circle">
            <span class="logo-h">H</span>
            <span class="logo-imai">IMAI</span>
        </div>
        <div class="title-text-box">
            <div class="header-title">今井社会保険労務士事務所</div>
            <div class="header-subtitle">就業規則・労務リスク判定 AIアシスタント</div>
        </div>
    </div>
    
    <div class="footer">
        © 2024 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office
    </div>
    """, unsafe_allow_html=True)

# --- 3. Dify API 設定 ---
try:
    DIFY_API_KEY = st.secrets["DIFY_API_KEY"]
except KeyError:
    st.error("Secretsに DIFY_API_KEY が設定されていません。")
    st.stop()

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
        placeholder.markdown("🔍 判定中...")
        
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
            st.error(f"接続エラー: {e}")