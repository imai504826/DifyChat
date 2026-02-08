import streamlit as st
import requests
import json

# --- 1. ページ設定（ブラウザのタブ名など） ---
st.set_page_config(page_title="労務リスク判定AI", layout="centered")

# --- 2. デザインを整えるCSS（魔法のコード） ---
st.markdown("""
    <style>
    /* メインタイトルの装飾 */
    .main-title {
        font-size: 32px;
        font-weight: bold;
        color: #1E3A8A; /* 濃い紺色 */
        text-align: center;
        padding: 20px;
        border-bottom: 2px solid #1E3A8A;
        margin-bottom: 30px;
    }
    /* 全体の背景を少しグレーにしてプロっぽく */
    .stApp {
        background-color: #f8fafc;
    }
    </style>
    <div class="main-title">⚖️ 労務リスク判定 AIアシスタント</div>
    """, unsafe_allow_html=True)

# --- 3. API設定 (Streamlit Secretsから読み込み) ---
DIFY_API_KEY = st.secrets["DIFY_API_KEY"]
DIFY_ENDPOINT = "https://api.dify.ai/v1/chat-messages"

# --- 4. セッション状態（履歴）の初期化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = ""

# --- 5. 過去のチャット履歴を表示 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. ユーザー入力とAPI呼び出し ---
if prompt := st.chat_input("就業規則の条文などを入力してください..."):
    # ユーザーの入力を画面に表示 & 履歴保存
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Dify APIへリクエスト送信
    with st.chat_message("assistant"):
        response_placeholder = st.empty() # ローディング表示用
        
        headers = {
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": {},
            "query": prompt,
            "response_mode": "blocking",
            "user": "default_user",
            "conversation_id": st.session_state.conversation_id
        }

        try:
            response = requests.post(DIFY_ENDPOINT, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            answer = data.get("answer", "返信がありませんでした。")
            
            if "conversation_id" in data:
                st.session_state.conversation_id = data["conversation_id"]

            # AIの回答を表示 & 履歴保存
            response_placeholder.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")