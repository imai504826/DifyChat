import streamlit as st
import requests
import uuid
from auth import check_password, logout

# --- 1. ページ設定 ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="⚖️", layout="centered")

# --- 2. 認証チェック ---
if check_password():
    
    # --- CSS: 構造を整理し、入力エリアとフッターを完全同期 ---
    st.markdown("""
        <style>
        /* 全体背景 */
        .stApp { background-color: #f9f9fb; }
        
        /* メインコンテンツ幅の固定 */
        .block-container {
            max-width: 730px !important;
            padding-bottom: 150px !important; 
        }

        /* --- 下部固定エリア：標準コンテナのデザインを上書き --- */
        
        /* 入力エリアの背景（白い帯）と枠線 */
        [data-testid="stChatFloatingInputContainer"] {
            background-color: #ffffff !important;
            border-top: 1px solid #eaeaea !important;
            padding: 20px 0 45px 0 !important; /* 下部にCopyRight用のスペースを確保 */
            left: 0 !important;
            right: 0 !important;
        }

        /* 入力ボックスのデザインを整え、不要な枠を消す */
        [data-testid="stChatInput"] {
            max-width: 690px !important;
            margin: 0 auto !important;
            border: 1px solid #e0e0e0 !important;
            border-radius: 8px !important;
            background-color: #fcfcfc !important;
        }
        
        [data-testid="stChatInput"] > div {
            border: none !important;
            box-shadow: none !important;
        }

        /* --- CopyRightを疑似要素（::after）で強制表示 --- */
        /* これにより、サイドバーの動きと100%連動し、消えることもありません */
        [data-testid="stChatFloatingInputContainer"]::after {
            content: "© 2026 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office";
            position: absolute;
            bottom: 15px;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 10px;
            color: #888888;
            font-family: sans-serif;
        }
        </style>
        """, unsafe_allow_html=True)

    # --- ヘッダー（幅730px固定） ---
    st.markdown("""
        <div style="background-color: #ffffff; padding: 25px 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #eaeaea; margin-bottom: 30px; max-width: 730px; margin-left: auto; margin-right: auto;">
            <div style="display: flex; align-items: center;">
                <div style="width: 58px; height: 58px; background-color: #061e3d; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-right: 20px; flex-shrink: 0;">
                    <span style="color: #ffffff; font-size: 26px; font-weight: 900; line-height: 1;">H</span>
                    <span style="font-size: 9px; font-weight: bold; color: #ffffff; margin-top: -2px;">IMAI</span>
                </div>
                <div>
                    <div style="color: #061e3d; font-size: 21px; font-weight: 700; line-height: 1.2;">今井社会保険労務士事務所</div>
                    <div style="color: #666666; font-size: 13.5px; margin-top: 2px;">就業規則・労務リスク判定 AIアシスタント</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        logout()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- チャット入力 ---
    if prompt := st.chat_input("就業規則の条文を入力してください..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.status("🔍 解析・判定中...", expanded=True) as status:
                try:
                    D_KEY = st.secrets["DIFY_API_KEY"]
                    response = requests.post(
                        "https://api.dify.ai/v1/chat-messages",
                        headers={"Authorization": f"Bearer {D_KEY}", "Content-Type": "application/json"},
                        json={"inputs": {}, "query": prompt, "response_mode": "blocking", "user": st.session_state.user_id},
                        timeout=120
                    )
                    response.raise_for_status()
                    answer = response.json().get("answer", "回答を取得できませんでした。")
                    status.update(label="✅ 判定完了", state="complete", expanded=False)
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    status.update(label="❌ エラー", state="error")
                    st.error("システムエラーが発生しました。")