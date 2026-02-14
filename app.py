import streamlit as st
import requests
import uuid
import os
import json
import base64
from auth import check_password, logout

# --- 1. 定数・設定管理 ---
DIFY_API_URL = "https://api.dify.ai/v1/chat-messages"
LOGO_IMAGE = "image/CSI&LC IMAIのロゴ.jpg"

def init_page_style():
    """デザイン・CSSの初期化（モバイル最適化）"""
    st.set_page_config(page_title="労務リスク判定 AI", page_icon="🌿", layout="centered")
    st.markdown("""
        <style>
        .stApp { background-color: #fcfbf9; }
        /* モバイルで入力欄が隠れないようパディング調整 */
        .block-container { max-width: 800px !important; padding-bottom: 150px !important; }
        
        /* サイドバーのログアウトボタンを強調 */
        section[data-testid="stSidebar"] .stButton > button {
            width: 100%;
            border-radius: 10px;
            color: #d9534f;
            border: 1px solid #ffeded;
            background-color: #fff5f5;
        }

        /* ヘッダーの装飾 */
        .header-box {
            background-color: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.02);
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .footer { position: fixed; bottom: 10px; left: 0; width: 100%; text-align: center; color: #b0b0c0; font-size: 10px; z-index: 0; }
        </style>
        <div class="footer">© 2026 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office</div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """サイドバーに操作系を集約（スマホで押しやすい）"""
    with st.sidebar:
        st.markdown("### ⚙️ 設定")
        if st.button("ログアウト", key="sidebar_logout"):
            logout()
        st.divider()
        st.caption("Ver 2.0 (Responsive)")

def render_header():
    """ヘッダー：タイトルとロゴに専念（ボタンを排除してスッキリ）"""
    logo_html = ""
    if os.path.exists(LOGO_IMAGE):
        with open(LOGO_IMAGE, "rb") as f:
            data = base64.b64encode(f.read()).decode()
            logo_html = f'<img src="data:image/jpg;base64,{data}" width="60" style="border-radius:8px;">'

    st.markdown(f"""
        <div class="header-box">
            {logo_html}
            <div>
                <div style="font-size: 18px; font-weight: bold; color: #2d4059; line-height: 1.2;">
                    今井久一郎<br>社会保険労務士事務所
                </div>
                <div style="font-size: 11px; color: #8899a6; margin-top: 4px;">
                    就業規則・労務リスク判定 AIアシスタント
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 2. 通信・メイン処理 ---
def call_dify_api(query, user_id):
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

    render_sidebar() # サイドバーにログアウトを配置
    render_header()  # ヘッダーは表示のみ

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