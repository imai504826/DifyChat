import streamlit as st
import requests
import uuid
from auth import check_password, logout

# --- 1. ページ設定 ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="⚖️", layout="centered")

# --- 2. 認証チェック ---
if check_password():
    
    # --- CSS: 徹底したクリーンアップと整列 ---
    st.markdown("""
        <style>
        /* 全体背景と基本設定 */
        .stApp { background-color: #f9f9fb; }
        
        /* メインコンテンツ幅をヘッダー(730px)に厳密に合わせる */
        .block-container {
            max-width: 730px !important;
            padding-top: 3rem !important;
            padding-bottom: 160px !important;
        }

        /* --- 下部固定エリアの再構築（無駄な線を排除） --- */

        /* 1. 土台となる白い帯（境界線を1本のみに限定） */
        .custom-footer-bg {
            position: fixed;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 100%;
            max-width: 730px;
            height: 140px;
            background-color: #ffffff;
            border-top: 1px solid #eaeaea; /* これ以外の枠線は不要 */
            z-index: 90;
            pointer-events: none;
        }

        /* 2. 入力エリアの調整（標準の枠線や背景をリセット） */
        [data-testid="stChatFloatingInputContainer"] {
            background-color: transparent !important;
            border: none !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: 100% !important;
            max-width: 730px !important;
            bottom: 60px !important;
            z-index: 100 !important;
            box-shadow: none !important;
        }

        /* 入力ボックス内部：以前の赤い線や無駄な枠を完全に上書き */
        [data-testid="stChatInput"] {
            border: 1px solid #e0e0e0 !important;
            border-radius: 8px !important;
            background-color: #fcfcfc !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
        }

        /* テキストエリア自体の枠線を消去（これが赤い枠の原因になりやすい） */
        [data-testid="stChatInput"] textarea {
            border: none !important;
            box-shadow: none !important;
        }

        /* 3. 免責事項・コピーライト */
        .custom-footer-content {
            position: fixed;
            bottom: 12px;
            left: 50%;
            transform: translateX(-50%);
            width: 100%;
            max-width: 730px;
            text-align: center;
            z-index: 101;
            font-family: sans-serif;
        }

        .footer-red-notice {
            color: #d93025;
            font-size: 11px;
            font-weight: 700;
            margin-bottom: 2px;
            letter-spacing: 0.02em;
        }
        .footer-copyright {
            color: #888888;
            font-size: 9px;
        }

        /* --- サイドバー開閉時の微調整 --- */
        /* サイドバーがある時でも、常にメインエリアの中央に吸い付くように設定 */
        section[data-testid="stSidebar"][aria-expanded="true"] ~ .main .custom-footer-bg,
        section[data-testid="stSidebar"][aria-expanded="true"] ~ .main .custom-footer-content {
            /* Streamlitの標準挙動に合わせ自動計算されるため、特殊なleft指定を排除 */
        }
        
        /* デバッグ用の赤い線を強制削除 */
        div.stChatInputContainer {
            border: none !important;
        }
        </style>
        <div class="custom-footer-bg"></div>
        """, unsafe_allow_html=True)

    # --- ヘッダー（幅730px固定） ---
    st.markdown("""
        <div style="background-color: #ffffff; padding: 25px 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #eaeaea; margin-bottom: 30px;">
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

    # メッセージ表示
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

    # --- 下部コンテンツ ---
    st.markdown("""
        <div class="custom-footer-content">
            <div class="footer-red-notice">
                【免責事項】本AIの回答は法的助言ではありません。最終判断は必ず専門家へ相談の上、自己責任で行ってください。
            </div>
            <div class="footer-copyright">
                © 2026 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office
            </div>
        </div>
    """, unsafe_allow_html=True)