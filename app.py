import streamlit as st
import requests
import uuid
from auth import check_password, logout

# --- 1. ページ設定 ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="⚖️", layout="centered")

# --- 2. 認証チェック ---
if check_password():
    
    # --- CSS: ミリ単位のズレと「奥の残像」を完全消去 ---
    st.markdown("""
        <style>
        .stApp { background-color: #f9f9fb; }
        
        /* メイン幅固定 */
        .block-container {
            max-width: 730px !important;
            padding-top: 3rem !important;
            padding-bottom: 160px !important;
        }

        /* --- 【決定版】下部ユニットの完全カプセル化 --- */

        /* 1. 全てを包むコンテナ：これ自体を中央に1つだけ置く */
        .ultra-footer-wrapper {
            position: fixed;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 100%;
            max-width: 730px; /* ヘッダー幅と厳密一致 */
            height: 150px;
            z-index: 9999;
            pointer-events: none; /* 下の要素を邪魔しない */
        }

        /* 2. 内部の白い背景：wrapperの中にあるので、もうズレようがない */
        .inner-white-plate {
            width: 100%;
            height: 100%;
            background-color: #ffffff;
            border-top: 1px solid #eaeaea;
            position: absolute;
            top: 0;
            left: 0;
            z-index: 1;
        }

        /* 3. 入力欄の強制上書き：標準の浮遊枠を無効化 */
        [data-testid="stChatFloatingInputContainer"] {
            position: absolute !important;
            bottom: 70px !important; /* wrapper底面からの距離 */
            left: 0 !important;
            right: 0 !important;
            width: 95% !important; /* 少し内側に */
            margin: 0 auto !important;
            background: transparent !important;
            border: none !important;
            z-index: 2 !important;
            transform: none !important; /* 親がズレを吸収するため不要 */
        }

        /* 入力ボックス自体の枠（以前の赤い枠や不明な枠を消去） */
        [data-testid="stChatInput"] {
            border: 1px solid #e0e0e0 !important;
            border-radius: 8px !important;
            background-color: #fcfcfc !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.03) !important;
        }
        
        /* 内部の「不明なテキスト枠」の原因（標準textareaの枠）を殺す */
        [data-testid="stChatInput"] div, [data-testid="stChatInput"] textarea {
            border: none !important;
            box-shadow: none !important;
        }

        /* 4. CopyRight：これもwrapperの中に閉じ込める */
        .inner-footer-text {
            position: absolute;
            bottom: 15px;
            width: 100%;
            text-align: center;
            z-index: 3;
        }

        .notice-red {
            color: #d93025;
            font-size: 11px;
            font-weight: 700;
            margin-bottom: 2px;
            display: block;
        }
        .copyright-gray {
            color: #888888;
            font-size: 9px;
            display: block;
        }
        </style>
        
        <div class="ultra-footer-wrapper">
            <div class="inner-white-plate"></div>
            <div class="inner-footer-text">
                <span class="notice-red">【免責事項】本AIの回答は法的助言ではありません。最終判断は必ず専門家へ相談の上、自己責任で行ってください。</span>
                <span class="copyright-gray">© 2026 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office</span>
            </div>
        </div>
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