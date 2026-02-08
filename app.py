import streamlit as st
import requests
import uuid
from auth import check_password, logout

# --- 1. ページ設定 ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="⚖️", layout="centered")

# --- 2. 認証チェック ---
if check_password():
    
    # --- CSS: 無駄な線を排除し、ヘッダーと完璧に整列させる ---
    st.markdown("""
        <style>
        /* 全体背景 */
        .stApp { background-color: #f9f9fb; }
        
        /* メインコンテンツ幅をヘッダーに固定 */
        .block-container {
            padding-top: 5rem !important;
            padding-bottom: 180px !important; 
            max-width: 730px !important;
        }

        /* --- 【決定版】下部エリアの統合デザイン --- */

        /* 1. 下部全体の白い「土台」：サイドバーを避けて配置 */
        .footer-unit-bg {
            position: fixed;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 100%;
            max-width: 730px; /* ヘッダーと完全一致 */
            height: 140px; /* 入力欄とフッターを収める高さ */
            background-color: #ffffff;
            border-top: 1px solid #eaeaea;
            box-shadow: 0 -5px 15px rgba(0,0,0,0.03);
            z-index: 100;
        }

        /* 2. 入力エリアの調整：無駄な背景色や枠線を消して統合 */
        [data-testid="stChatInput"] {
            position: fixed !important;
            bottom: 60px !important; /* フッターのすぐ上 */
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: 100% !important;
            max-width: 700px !important; /* 内側に少しマージン */
            background-color: transparent !important; /* 灰色を廃止し白に統合 */
            border: none !important;
            padding: 0 !important;
            z-index: 101 !important;
        }
        
        /* 入力ボックス内の影や境界線を微調整 */
        [data-testid="stChatInput"] textarea {
            border: 1px solid #e0e0e0 !important;
        }

        /* 3. フッターテキスト（免責事項） */
        .footer-text-area {
            position: absolute;
            bottom: 15px;
            width: 100%;
            text-align: center;
        }

        .footer-red-text {
            color: #d93025;
            font-size: 11px;
            font-weight: 700;
            margin-bottom: 3px;
            padding: 0 20px;
        }
        .footer-copy-text {
            color: #888888;
            font-size: 9px;
        }

        /* 無駄な標準線を消去 */
        [data-testid="stHeader"] { background: rgba(0,0,0,0); }
        .stChatFloatingInputContainer { background-color: transparent !important; border: none !important; }
        </style>
        """, unsafe_allow_html=True)

    # --- ヘッダー（幅730px） ---
    st.markdown("""
        <div style="background-color: #ffffff; padding: 25px 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #eaeaea; margin-bottom: 40px; max-width: 730px; margin-left: auto; margin-right: auto;">
            <div style="display: flex; align-items: center;">
                <div style="width: 60px; height: 60px; background-color: #061e3d; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-right: 20px;">
                    <span style="color: #ffffff; font-size: 28px; font-weight: 900;">H</span>
                    <span style="font-size: 9px; font-weight: bold; color: #ffffff; margin-top: -2px;">IMAI</span>
                </div>
                <div>
                    <div style="color: #061e3d; font-size: 22px; font-weight: 700;">今井社会保険労務士事務所</div>
                    <div style="color: #666666; font-size: 14px;">就業規則・労務リスク判定 AIアシスタント</div>
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

    # --- チャット入力（CSSで位置制御） ---
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

    # --- 下部ユニット（白背景に全てを統合） ---
    st.markdown("""
        <div class="footer-unit-bg">
            <div class="footer-text-area">
                <div class="footer-red-text">
                    【免責事項】本AIの回答は法的助言ではありません。最終判断は必ず専門家へ相談の上、自己責任で行ってください。
                </div>
                <div class="footer-copy-text">
                    © 2024 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)