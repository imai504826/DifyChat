import streamlit as st
import requests
import uuid
from auth import check_password, logout

# --- 1. ページ設定 (これは最初に行う必要があります) ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="⚖️", layout="centered")

# --- 2. 認証チェック (これが最優先) ---
# ログインしていない場合は、この下のコードは一切読み込まれません
if check_password():
    
    # --- 3. ログイン後のみ表示されるデザイン ---
    st.markdown("""
        <style>
        .stApp { background-color: #ffffff; }
        .header-container {
            display: flex; align-items: center; justify-content: flex-start;
            padding: 80px 20px 20px 0; border-bottom: 2px solid #f0f2f6; margin-bottom: 30px;
        }
        .logo-circle {
            width: 60px; height: 60px; background: #061e3d; border-radius: 50%;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            margin-right: 20px; flex-shrink: 0;
        }
        .logo-h { color: #ffffff; font-size: 28px; font-weight: 900; font-family: 'Georgia', serif; line-height: 1; }
        .logo-imai { font-size: 8px; font-weight: bold; color: #ffffff; margin-top: -2px; }
        .header-title { color: #061e3d; font-size: 22px; font-weight: 700; margin: 0; }
        .header-subtitle { color: #666666; font-size: 13px; margin-top: 4px; }
        .footer {
            position: fixed; bottom: 0; left: 0; width: 100%;
            background-color: #061e3d; color: white; text-align: center;
            padding: 10px 0; font-size: 11px; z-index: 100;
        }
        .block-container { padding-top: 0rem !important; padding-bottom: 6rem !important; }
        </style>
        
        <div class="header-container">
            <div class="logo-circle"><span class="logo-h">H</span><span class="logo-imai">IMAI</span></div>
            <div class="title-text-box">
                <div class="header-title">今井社会保険労務士事務所</div>
                <div class="header-subtitle">就業規則・労務リスク判定 AIアシスタント</div>
            </div>
        </div>
        <div class="footer">© 2024 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office</div>
        """, unsafe_allow_html=True)

    logout() # ログイン後のみサイドバーにログアウトを表示

    # --- 4. Dify API 連携 ---
    try:
        D_KEY = st.secrets["DIFY_API_KEY"]
    except:
        st.error("APIキーが設定されていません。")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("就業規則の条文を入力してください..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            res_box = st.empty()
            res_box.markdown("🔍 判定中...")
            try:
                response = requests.post(
                    "https://api.dify.ai/v1/chat-messages",
                    headers={"Authorization": f"Bearer {D_KEY}", "Content-Type": "application/json"},
                    json={"inputs": {}, "query": prompt, "response_mode": "blocking", "user": st.session_state.user_id},
                    timeout=60
                )
                answer = response.json().get("answer", "エラー")
                res_box.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"エラー: {e}")