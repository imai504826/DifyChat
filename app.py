import streamlit as st
import requests
import uuid
import os
import json
from auth import check_password, logout

# --- 1. 定数・設定管理 ---
DIFY_API_URL = "https://api.dify.ai/v1/chat-messages"
LOGO_IMAGE = "image/CSI&LC IMAIのロゴ.jpg"

def init_page_style():
    """デザイン・CSSの初期化（モバイル対応）"""
    st.set_page_config(page_title="労務リスク判定 AI", page_icon="🌿", layout="centered")
    st.markdown("""
        <style>
        .stApp { background-color: #fcfbf9; }
        .block-container { max-width: 800px !important; padding-bottom: 120px !important; }
        
        /* ヘッダー全体のコンテナ */
        .custom-header {
            background-color: white;
            padding: 15px;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.02);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between; /* 両端に寄せる */
        }
        
        /* 左側（ロゴとタイトル）のグループ */
        .header-left {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .header-titles {
            display: flex;
            flex-direction: column;
        }

        /* ログアウトボタンのスタイル */
        div.stButton > button {
            background-color: white;
            color: #7d8c9e;
            border: 1px solid #e0e0e0;
            border-radius: 20px;
            font-size: 11px;
            padding: 0.2rem 0.8rem;
        }

        /* モバイル用フォントサイズ調整 */
        @media (max-width: 640px) {
            .title-text { font-size: 16px !important; }
            .subtitle-text { font-size: 10px !important; }
            .header-left { gap: 10px; }
        }

        .footer { position: fixed; bottom: 10px; left: 0; width: 100%; text-align: center; color: #b0b0c0; font-size: 10px; z-index: 100; }
        </style>
        <div class="footer">© 2026 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office</div>
    """, unsafe_allow_html=True)

def render_header():
    """モバイルでも崩れないヘッダーの表示"""
    # st.columnsを使わず、HTML/CSSで構造を固定
    logo_html = ""
    if os.path.exists(LOGO_IMAGE):
        import base64
        with open(LOGO_IMAGE, "rb") as f:
            data = base64.b64encode(f.read()).decode()
            logo_html = f'<img src="data:image/jpg;base64,{data}" width="50">'
    else:
        logo_html = '<div style="width:50px;"></div>'

    st.markdown(f"""
        <div class="custom-header">
            <div class="header-left">
                {logo_html}
                <div class="header-titles">
                    <span class="title-text" style="font-size: 18px; font-weight: bold; color: #2d4059; line-height: 1.2;">
                        今井久一郎<br>社会保険労務士事務所
                    </span>
                    <span class="subtitle-text" style="font-size: 11px; color: #8899a6;">
                        就業規則・労務リスク判定 AI
                    </span>
                </div>
            </div>
            <div id="logout-placeholder"></div>
        </div>
    """, unsafe_allow_html=True)
    
    # ログアウトボタンだけはStreamlitの機能を使う必要があるため、
    # サイドバー上部や特定の位置に配置するか、columnsでボタン専用枠を確保
    col_empty, col_btn = st.columns([5, 1.5])
    with col_btn:
        if st.button("ログアウト", key="header_logout"):
            logout()

def call_dify_api(query, user_id):
    """Dify APIとの通信"""
    try:
        api_key = st.secrets["DIFY_API_KEY"]
        payload = {"inputs": {}, "query": query, "response_mode": "streaming", "user": user_id}
        response = requests.post(DIFY_API_URL, headers={"Authorization": f"Bearer {api_key}"}, json=payload, stream=True, timeout=150)
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                line_str = line.decode("utf-8")
                if line_str.startswith("data:"): yield json.loads(line_str[5:])
    except Exception as e:
        st.error(f"接続エラー: {str(e)}")

def main():
    init_page_style()
    if not check_password(): return

    render_header()

    if "messages" not in st.session_state: st.session_state.messages = []
    if "user_id" not in st.session_state: st.session_state.user_id = str(uuid.uuid4())

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("就業規則の条文を入力してください..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            full_answer = ""
            answer_placeholder = st.empty()
            with st.status("🌿 解析中...", expanded=True) as status:
                for data in call_dify_api(prompt, st.session_state.user_id):
                    if data.get("event") == "message":
                        full_answer += data.get("answer", "")
                        answer_placeholder.markdown(full_answer + " ▌")
                    elif data.get("event") == "message_end":
                        status.update(label="✨ 判定完了", state="complete", expanded=False)
            answer_placeholder.markdown(full_answer)
            st.session_state.messages.append({"role": "assistant", "content": full_answer})

if __name__ == "__main__":
    main()