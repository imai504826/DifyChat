import streamlit as st
# --- デザインを整える魔法のコード ---
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
    /* 判定結果（STEP1）の強調 */
    .risk-box {
        background-color: #FEE2E2; /* 薄い赤 */
        border-left: 5px solid #DC2626; /* 濃い赤 */
        padding: 15px;
        border-radius: 5px;
    }
    </style>
    <div class="main-title">労務リスク判定 AIアシスタント</div>
    """, unsafe_allow_html=True)
import requests
import json

# --- 1. ページ設定 ---
st.set_page_config(page_title="My AI SaaS", layout="centered")
st.title("🤖 カスタムAIチャット")

# --- 2. API設定 (Streamlit Secretsから読み込み) ---
# 後ほどStreamlit Cloudの設定画面で "DIFY_API_KEY" を登録します
DIFY_API_KEY = st.secrets["DIFY_API_KEY"]
DIFY_ENDPOINT = "https://api.dify.ai/v1/chat-messages"

# --- 3. セッション状態（履歴）の初期化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = ""

# --- 4. 過去のチャット履歴を表示 ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. ユーザー入力とAPI呼び出し ---
if prompt := st.chat_input("メッセージを入力してください..."):
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
            "response_mode": "blocking", # SaaS初期はblockingが簡単
            "user": "default_user", # 本来はログインユーザーIDを入れる
            "conversation_id": st.session_state.conversation_id
        }

        try:
            response = requests.post(DIFY_ENDPOINT, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            answer = data.get("answer", "返信がありませんでした。")
            
            # 会話IDを更新（これで文脈が繋がる）
            if "conversation_id" in data:
                st.session_state.conversation_id = data["conversation_id"]

            # AIの回答を表示 & 履歴保存
            response_placeholder.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")