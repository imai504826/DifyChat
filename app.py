import streamlit as st
import requests
import uuid
from auth import check_password, logout

# --- 1. ページ設定 ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="⚖️", layout="centered")

# --- 2. 認証チェック ---
if check_password():
    
    # --- CSS: サイドバーの状態に合わせて動的に位置を調整 ---
    st.markdown("""
        <style>
        .stApp { background-color: #f9f9fb; }
        
        /* メインコンテンツの幅設定 */
        .block-container {
            padding-top: 5rem !important;
            padding-bottom: 180px !important; 
            max-width: 730px !important;
        }

        /* --- 重要：固定要素をメインエリア内に封じ込める --- */
        
        /* 1. グレーの入力帯をメインエリアに合わせて配置 */
        [data-testid="stChatInput"] {
            position: fixed !important;
            bottom: 60px !important;
            /* 画面端ではなく、親要素の幅を基準にする設定 */
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: 100% !important;
            max-width: 100vw !important;
            background-color: #f0f2f6 !important;
            padding: 15px 0 !important;
            z-index: 99 !important;
            border-top: 1px solid #e6e9ef !important;
        }

        /* 入力ボックス自体をヘッダーの幅(730px)と完全に同期 */
        [data-testid="stChatInput"] > div {
            width: 90% !important; /* 余裕を持たせる */
            max-width: 730px !important;
            margin: 0 auto !important;
        }

        /* 2. 白いフッターを最下部に配置（サイドバーを避けるため.main内に配置されるように調整） */
        .white-footer-panel {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 60px;
            background-color: #ffffff !important;
            border-top: 1px solid #eaeaea;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 100;
        }
        
        /* サイドバーが開いている時、フッターを右側に寄せる（Streamlitの標準挙動に合わせる） */
        [data-testid="stSidebar"][aria-expanded="true"] ~ .main .white-footer-panel {
            left: 260px; /* サイドバーの標準幅分 */
            width: calc(100% - 260px);
        }

        .footer-red-text {
            color: #d93025;
            font-size: 11px;
            font-weight: 700;
            margin-bottom: 2px;
            text-align: center;
        }
        .footer-copy-text {
            color: #888888;
            font-size: 9px;
        }
        </style>
        """, unsafe_allow_html=True)

    # --- ヘッダー（幅を厳密に730pxで固定） ---
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

    # --- 最下部の独立した白いフッター ---
    st.markdown("""
        <div class="white-footer-panel">
            <div class="footer-red-text">
                【免責事項】本AIの回答は法的助言ではありません。最終判断は必ず専門家へ相談の上、自己責任で行ってください。
            </div>
            <div class="footer-copy-text">
                © 2024 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office
            </div>
        </div>
    """, unsafe_allow_html=True)