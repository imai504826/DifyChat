import streamlit as st
import requests
import uuid
from auth import check_password, logout

# --- 1. ページ設定 ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="⚖️", layout="centered")

# --- 2. 認証チェック ---
if check_password():
    
    # --- デザインCSS（添付イメージに近いブルー背景） ---
    st.markdown("""
        <style>
        /* 背景色を鮮やかなブルーに設定 */
        .stApp {
            background-color: #007bff; /* ロイヤルブルー */
        }
        
        /* メインコンテンツを白いカード状にする */
        .main-card {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            margin-top: 20px;
        }
        
        /* ヘッダーエリア */
        .header-container {
            display: flex;
            align-items: center;
            justify-content: flex-start;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f2f6;
            margin-bottom: 25px;
        }
        
        /* ロゴの円形デザイン */
        .logo-box {
            width: 60px;
            height: 60px;
            background-color: #061e3d;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            flex-shrink: 0;
        }
        .logo-h { color: #ffffff; font-size: 28px; font-weight: 900; font-family: 'Georgia', serif; line-height: 1; }
        .logo-imai { font-size: 8px; font-weight: bold; color: #ffffff; margin-top: -2px; letter-spacing: 1px; }

        .header-title { color: #061e3d; font-size: 22px; font-weight: 700; margin: 0; line-height: 1.2; }
        .header-subtitle { color: #666666; font-size: 13px; margin-top: 2px; }
        
        /* 重要事項（免責）ボックス - イメージ通りの青枠 */
        .disclaimer-box {
            background-color: #f0f7ff;
            border: 2px solid #007bff;
            padding: 15px;
            margin: 15px 0 20px 0;
            border-radius: 10px;
        }
        .disclaimer-text {
            color: #004085;
            font-size: 11px;
            line-height: 1.6;
            margin: 0;
        }

        /* フッター（白背景に変更して見やすく） */
        .footer {
            margin-top: 30px;
            background-color: #ffffff;
            color: #061e3d;
            text-align: center;
            padding: 15px 0;
            font-size: 12px;
            border-radius: 10px;
            font-weight: 600;
        }

        /* チャットエリアの余白調整 */
        .stChatMessage { background-color: #f8f9fa !important; border-radius: 10px; margin-bottom: 10px; }
        
        /* 入力欄の浮き上がり */
        .stChatInputContainer { padding-bottom: 20px; }
        </style>
        """, unsafe_allow_html=True)

    # 白いカードの開始（HTMLタグ）
    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    # ヘッダー表示
    st.markdown("""
        <div class="header-container">
            <div class="logo-box">
                <span class="logo-h">H</span>
                <span class="logo-imai">IMAI</span>
            </div>
            <div class="title-text-box">
                <div class="header-title">今井久一郎社会保険労務士事務所</div>
                <div class="header-subtitle">就業規則・労務リスク判定 AIアシスタント</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    logout()

    # --- 重要事項（免責）関数 ---
    def display_disclaimer():
        st.markdown("""
            <div class="disclaimer-box">
                <p class="disclaimer-text">
                    <strong>【AI判定に関する重要事項】</strong><br>
                    本システムは、当事務所が監修した<strong>最新の就業規則ナレッジ（RAG）を直接参照</strong>しており、一般的なAIに比べ高い正確性を備えています。<br>
                    しかしながら、本回答はAIによる推論であり法的助言を確定させるものではありません。個別の事案に対する最終的な判断については、必ず当事務所の社会保険労務士にご確認ください。
                </p>
            </div>
        """, unsafe_allow_html=True)

    # --- Dify API 設定 ---
    try:
        D_KEY = st.secrets["DIFY_API_KEY"]
    except:
        st.error("APIキーが設定されていません。")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())

    # --- 履歴の表示 ---
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
            res_box = st.empty()
            res_box.markdown("🔍 判定中...")
            try:
                response = requests.post(
                    "https://api.dify.ai/v1/chat-messages",
                    headers={"Authorization": f"Bearer {D_KEY}", "Content-Type": "application/json"},
                    json={"inputs": {}, "query": prompt, "response_mode": "blocking", "user": st.session_state.user_id},
                    timeout=60
                )
                response.raise_for_status()
                answer = response.json().get("answer", "回答を取得できませんでした。")
                
                res_box.markdown(answer)
                display_disclaimer()
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except