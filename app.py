import streamlit as st
import requests
import uuid
from auth import check_password, logout

# --- 1. ページ設定 ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="⚖️", layout="centered")

# --- 2. 認証チェック ---
if check_password():
    
    # --- CSS: ヘッダー、入力欄、フッターを垂直に完璧に揃える ---
    st.markdown("""
        <style>
        /* アプリ全体の背景 */
        .stApp { background-color: #f9f9fb; }
        
        /* コンテンツ幅を 730px に統一 */
        .block-container {
            max-width: 730px !important;
            padding-top: 4rem !important;
            padding-bottom: 180px !important;
        }

        /* --- 下部固定ユニットのデザイン --- */

        /* 背面の白いプレート（ヘッダーと同じ幅で中央固定） */
        .fixed-footer-base {
            position: fixed;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 100%;
            max-width: 730px; /* ヘッダーと完全一致 */
            height: 150px;
            background-color: #ffffff;
            border-top: 1px solid #eaeaea;
            box-shadow: 0 -5px 15px rgba(0,0,0,0.03);
            z-index: 90;
            pointer-events: none; /* 下の要素の邪魔をしない */
        }

        /* Streamlit標準の入力欄コンテナを調整 */
        [data-testid="stChatFloatingInputContainer"] {
            background-color: transparent !important;
            border: none !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: 100% !important;
            max-width: 730px !important;
            padding: 0 15px !important;
            bottom: 65px !important; /* 免責事項の上に配置 */
            z-index: 100 !important;
        }

        /* 入力ボックス内の装飾（無駄な線を消す） */
        [data-testid="stChatInput"] {
            border-radius: 10px !important;
            border: 1px solid #e0e0e0 !important;
            background-color: #fcfcfc !important;
        }

        /* フッターテキストの配置 */
        .footer-text-unit {
            position: fixed;
            bottom: 15px;
            left: 50%;
            transform: translateX(-50%);
            width: 100%;
            max-width: 730px;
            text-align: center;
            z-index: 101;
        }

        .footer-red-text {
            color: #d93025;
            font-size: 11px;
            font-weight: 700;
            margin-bottom: 2px;
        }
        .footer-copy-text {
            color: #888888;
            font-size: 9px;
        }

        /* サイドバーがある時の位置補正（Streamlit標準の挙動をサポート） */
        @media (min-width: 992px) {
            [data-testid="stSidebar"][aria-expanded="true"] ~ .main .fixed-footer-base,
            [data-testid="stSidebar"][aria-expanded="true"] ~ .main .footer-text-unit {
                margin-left: 0; /* 中央維持 */
            }
        }
        </style>
        
        <div class="fixed-footer-base"></div>
        """, unsafe_allow_html=True)

    # --- ヘッダー（幅730px固定） ---
    st.markdown("""
        <div style="background-color: #ffffff; padding: 25px 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #eaeaea; margin-bottom: 40px;">
            <div style="display: flex; align-items: center;">
                <div style="width: 58px; height: 58px; background-color: #061e3d; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-right: 20px; flex-shrink: 0;">
                    <span style="color: #ffffff; font-size: 26px; font-weight: 900; line-height: 1;">H</span>
                    <span style="font-size: 9px; font-weight: bold; color: #ffffff; margin-top: -2px;">IMAI</span>
                </div>
                <div>
                    <div style="color: #061e3d; font-size: 22px; font-weight: 700; line-height: 1.2;">今井社会保険労務士事務所</div>
                    <div style="color: #666666; font-size: 14px; margin-top: 2px;">就業規則・労務リスク判定 AIアシスタント</div>
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

    # --- チャット入力（標準機能を活かしつつ、CSSで中央固定） ---
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

    # --- 免責事項ユニット ---
    st.markdown("""
        <div class="footer-text-unit">
            <div class="footer-red-text">
                【免責事項】本AIの回答は法的助言ではありません。最終判断は必ず専門家へ相談の上、自己責任で行ってください。
            </div>
            <div class="footer-copy-text">
                © 2024 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office
            </div>
        </div>
    """, unsafe_allow_html=True)