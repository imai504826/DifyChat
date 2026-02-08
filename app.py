import streamlit as st
import requests
import uuid
from auth import check_password, logout

# --- 1. ページ設定 ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="⚖️", layout="centered")

# --- 2. 認証チェック ---
if check_password():
    
    # --- CSS: 下部エリアの統一と重なり解消 ---
    st.markdown("""
        <style>
        /* 全体の背景色 */
        .stApp { background-color: #f9f9fb; }
        
        /* 履歴エリア：下部に大きな余白を作り、固定エリアと被らせない */
        .block-container {
            padding-top: 5rem !important;
            padding-bottom: 220px !important; 
            max-width: 750px;
        }

        /* ヘッダーデザイン */
        .custom-header-card {
            background-color: #ffffff;
            padding: 25px 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border: 1px solid #eaeaea;
            margin-bottom: 40px;
        }
        .header-flex { display: flex; align-items: center; }
        .logo-box {
            width: 60px; height: 60px;
            background-color: #061e3d;
            border-radius: 50%;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            margin-right: 20px; flex-shrink: 0;
        }
        .logo-h { color: #ffffff; font-size: 28px; font-weight: 900; line-height: 1; }
        .logo-imai { font-size: 9px; font-weight: bold; color: #ffffff; margin-top: -2px; }

        /* 【解決策】入力欄とフッターを一つの白い「土台」に統一 */
        
        /* 1. Streamlit標準の入力コンテナの背景と影を消し、位置を固定 */
        [data-testid="stChatInput"] {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            bottom: 80px !important; /* フッターの上に浮かせる */
            z-index: 1001 !important;
        }

        /* 2. 下部全体を覆う「統一された白い帯」を作成 */
        .unified-bottom-panel {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 160px; /* 入力欄とフッターを包む十分な高さ */
            background-color: #ffffff;
            border-top: 1px solid #eaeaea;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            justify-content: flex-end; /* 下詰めで配置 */
            padding-bottom: 15px;
        }

        .footer-content-box {
            text-align: center;
            width: 100%;
        }
        
        .footer-red-text {
            color: #d93025;
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 4px;
        }
        .footer-copy-text {
            color: #888888;
            font-size: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

    def display_disclaimer():
        st.markdown(f"""
            <div style="background-color: #f8f9fa; border-left: 5px solid #061e3d; padding: 18px; margin: 15px 0; border-radius: 4px;">
                <p style="color: #444444; font-size: 12px; line-height: 1.7; margin: 0;">
                    <strong>【AI判定に関する重要事項】</strong><br>
                    本システムは、当事務所監修の最新ナレッジを参照していますが、最終判断は必ず当事務所の社会保険労務士にご確認ください。
                </p>
            </div>
        """, unsafe_allow_html=True)

    # --- ヘッダー ---
    st.markdown("""
        <div class="custom-header-card">
            <div class="header-flex">
                <div class="logo-box"><span class="logo-h">H</span><span class="logo-imai">IMAI</span></div>
                <div>
                    <div style="color: #061e3d; font-size: 24px; font-weight: 700;">今井社会保険労務士事務所</div>
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
            if msg["role"] == "assistant":
                display_disclaimer()

    # --- チャット入力 ---
    if prompt := st.chat_input("就業規則の条文を入力してください..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.status("🔍 条文を解析し、労務リスクを判定しています...", expanded=True) as status:
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
                    display_disclaimer()
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    status.update(label="❌ エラー", state="error")
                    st.error("システムエラーが発生しました。")

    # --- 【統一化の核心】すべての下部要素を一つの「白い土台」の上に載せる ---
    st.markdown("""
        <div class="unified-bottom-panel">
            <div class="footer-content-box">
                <div class="footer-red-text">
                    【免責事項】本AIの回答は法的助言ではありません。最終判断は必ず専門家へ相談の上、自己責任で行ってください。
                </div>
                <div class="footer-copy-text">
                    © 2024 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)