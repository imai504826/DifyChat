import streamlit as st
import requests
import uuid
from auth import check_password, logout

# --- 1. ページ設定 ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="⚖️", layout="centered")

# --- 2. 認証チェック ---
if check_password():
    
    # --- デザインCSS（重なりを構造的に排除） ---
    st.markdown("""
        <style>
        .stApp { background-color: #f9f9fb; }
        
        /* メインエリア：下部に大きな余白を確保 */
        .block-container {
            padding-top: 5rem !important;
            padding-bottom: 10rem !important; 
            max-width: 750px;
        }

        /* ヘッダーカード */
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
        .logo-h { color: #ffffff; font-size: 28px; font-weight: 900; font-family: 'Georgia', serif; line-height: 1; }
        .logo-imai { font-size: 9px; font-weight: bold; color: #ffffff; margin-top: -2px; }
        .header-title { color: #061e3d; font-size: 24px; font-weight: 700; margin: 0; }
        .header-subtitle { color: #666666; font-size: 14px; margin-top: 4px; }
        
        /* 回答内の免責ボックス */
        .disclaimer-box {
            background-color: #f8f9fa;
            border-left: 5px solid #061e3d;
            padding: 18px;
            margin: 15px 0;
            border-radius: 4px;
        }
        .disclaimer-text { color: #444444; font-size: 12px; line-height: 1.7; margin: 0; }

        /* 【ここが重要】入力欄自体にフッター要素を埋め込む */
        /* Streamlitの入力欄コンテナを背景として利用し、下部に余白を強制 */
        .stChatInputContainer {
            padding-bottom: 70px !important;
            background-color: #f9f9fb !important;
        }

        /* フッターを絶対配置ではなく、入力欄の下に「敷く」 */
        .custom-footer-content {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 70px; /* 固定高さを指定 */
            background-color: #ffffff; /* 入力欄との区別のため白背景 */
            border-top: 1px solid #eaeaea;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9; /* 入力欄(100以上)より低く設定 */
        }
        
        .footer-disclaimer {
            color: #d93025;
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 5px;
        }
        .footer-copyright {
            color: #888888;
            font-size: 11px;
        }
        </style>
        """, unsafe_allow_html=True)

    def display_disclaimer():
        st.markdown("""
            <div class="disclaimer-box">
                <p class="disclaimer-text">
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
                    <div class="header-title">今井社会保険労務士事務所</div>
                    <div class="header-subtitle">就業規則・労務リスク判定 AIアシスタント</div>
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

    # --- チャット入力エリア ---
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
                    status.update(label="❌ エラーが発生しました", state="error")
                    st.error("システムエラーが発生しました。時間を置いて再度お試しください。")

    # --- 重なりを物理的に不可能にするフッター配置 ---
    st.markdown("""
        <div class="custom-footer-content">
            <div class="footer-disclaimer">
                【免責事項】本AIの回答は法的助言ではありません。最終判断は必ず専門家に相談の上、自己責任で行ってください。
            </div>
            <div class="footer-copyright">
                © 2024 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office
            </div>
        </div>
    """, unsafe_allow_html=True)