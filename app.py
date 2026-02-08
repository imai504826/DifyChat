import streamlit as st
import requests
import uuid
from auth import check_password, logout

# --- 1. ページ設定 ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="⚖️", layout="centered")

# --- 2. 認証チェック ---
if check_password():
    
    # --- デザインCSS ---
    st.markdown("""
        <style>
        /* ページ全体の背景 */
        .stApp { background-color: #f9f9fb; }
        
        /* メインコンテナの余白調整（ヘッダー位置を適切に） */
        .block-container {
            padding-top: 4rem !important;
            padding-bottom: 8rem !important; /* フッターと被らないよう下部余白を確保 */
            max-width: 750px;
        }

        /* ヘッダーカード */
        .custom-header-card {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border: 1px solid #eaeaea;
            margin-bottom: 30px;
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

        .header-title { color: #061e3d; font-size: 22px; font-weight: 700; margin: 0; }
        .header-subtitle { color: #666666; font-size: 13px; margin-top: 4px; }
        
        /* チャット回答下の重要事項ボックス */
        .disclaimer-box {
            background-color: #f8f9fa;
            border-left: 5px solid #061e3d;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }
        .disclaimer-text { color: #444444; font-size: 11px; line-height: 1.6; margin: 0; }

        /* 【新設】画面最下部に固定するフッター（免責事項入り） */
        .footer-fixed {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #ffffff;
            color: #666666;
            text-align: center;
            padding: 12px 10px;
            font-size: 10px;
            border-top: 1px solid #eaeaea;
            z-index: 999;
            line-height: 1.5;
        }
        .footer-disclaimer {
            color: #888888;
            margin-bottom: 4px;
        }

        /* チャットメッセージの背景 */
        .stChatMessage {
            background-color: #ffffff !important;
            border: 1px solid #eaeaea !important;
            margin-bottom: 10px !important;
        }
        </style>
        """, unsafe_allow_html=True)

    # --- 重要事項（免責）表示関数（回答ごとに表示） ---
    def display_disclaimer():
        st.markdown("""
            <div class="disclaimer-box">
                <p class="disclaimer-text">
                    <strong>【AI判定に関する重要事項】</strong><br>
                    本システムは、当事務所が監修した最新の就業規則ナレッジ（RAG）を直接参照しており、一般的なAIに比べ高い正確性を備えています。<br>
                    しかしながら、本回答はAIによる推論であり法的助言を確定させるものではありません。個別の事案に対する最終的な判断については、必ず当事務所の社会保険労務士にご確認ください。
                </p>
            </div>
        """, unsafe_allow_html=True)

    # --- ヘッダー描画 ---
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

    # --- Dify 連携 ---
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
            if msg["role"] == "assistant":
                display_disclaimer()

    if prompt := st.chat_input("就業規則の条文を入力してください..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                response = requests.post(
                    "https://api.dify.ai/v1/chat-messages",
                    headers={"Authorization": f"Bearer {D_KEY}", "Content-Type": "application/json"},
                    json={"inputs": {}, "query": prompt, "response_mode": "blocking", "user": st.session_state.user_id},
                    timeout=60
                )
                answer = response.json().get("answer", "回答を取得できませんでした。")
                st.markdown(answer)
                display_disclaimer()
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"接続エラー: {e}")

    # --- フッター（最下部固定：免責事項とコピーライト） ---
    st.markdown("""
        <div class="footer-fixed">
            <div class="footer-disclaimer">
                【免責事項】本AIの回答は法的助言を構成するものではありません。最終的な判断は必ず専門家に相談の上、自己責任で行ってください。
            </div>
            <div>
                © 2024 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office
            </div>
        </div>
    """, unsafe_allow_html=True)