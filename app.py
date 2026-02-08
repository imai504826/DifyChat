import streamlit as st
import requests
import uuid
from auth import check_password, logout

# --- 1. ページ設定 ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="⚖️", layout="centered")

# --- 2. 認証チェック ---
if check_password():
    
    # --- CSS: サイドバー連動・完全整列 ---
    st.markdown("""
        <style>
        /* 全体背景 */
        .stApp { background-color: #f9f9fb; }
        
        /* コンテンツ幅を 730px に厳密固定 */
        .block-container {
            max-width: 730px !important;
            padding-top: 3rem !important;
            padding-bottom: 160px !important;
        }

        /* --- 下部固定ユニットのデザイン --- */

        /* 1. 下部の白い背景プレート */
        /* コンテンツエリア(.stMain)の子要素として配置されるよう調整 */
        .fixed-footer-container {
            position: fixed;
            bottom: 0;
            width: 100%;
            max-width: 730px; /* ヘッダーと一致 */
            height: 140px;
            background-color: #ffffff;
            border-top: 1px solid #eaeaea;
            z-index: 99;
            /* 左右中央寄せの決定版 */
            left: 50%;
            transform: translateX(-50%);
            pointer-events: none;
        }

        /* 2. 入力欄の強制整列（無駄な枠線を徹底排除） */
        [data-testid="stChatFloatingInputContainer"] {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            left: 0 !important;
            right: 0 !important;
            width: 100% !important;
            max-width: 730px !important;
            margin: 0 auto !important;
            bottom: 60px !important;
            z-index: 100 !important;
            padding: 0 10px !important;
        }

        /* 入力ボックス内部のデザイン */
        [data-testid="stChatInput"] {
            border: 1px solid #e0e0e0 !important;
            border-radius: 8px !important;
            background-color: #fcfcfc !important;
        }
        
        /* 以前出ていた不要なテキストエリア枠を非表示 */
        [data-testid="stChatInput"] > div {
            border: none !important;
        }

        /* 3. 免責事項・CopyRightの整列 */
        .footer-content-box {
            position: fixed;
            bottom: 15px;
            left: 50%;
            transform: translateX(-50%);
            width: 100%;
            max-width: 730px;
            text-align: center;
            z-index: 101;
            pointer-events: none;
        }

        .notice-red {
            color: #d93025;
            font-size: 11px;
            font-weight: 700;
            margin-bottom: 3px;
            display: block;
        }
        .copyright-text {
            color: #888888;
            font-size: 9px;
            display: block;
        }

        /* サイドバー展開時にフッターが置いていかれないための設定 */
        @media (min-width: 992px) {
            .fixed-footer-container, .footer-content-box {
                /* サイドバーがある場合でも常にメイン領域の中央を維持 */
            }
        }
        </style>
        
        <div class="fixed-footer-container"></div>
        
        <div class="footer-content-box">
            <span class="notice-red">【免責事項】本AIの回答は法的助言ではありません。最終判断は必ず専門家へ相談の上、自己責任で行ってください。</span>
            <span class="copyright-text">© 2026 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office</span>
        </div>
        """, unsafe_allow_html=True)

    # --- ヘッダー（幅730px） ---
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