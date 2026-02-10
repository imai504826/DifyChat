import streamlit as st
import requests
import uuid
import os
from auth import check_password, logout

# --- 1. ページ設定 ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="🌿", layout="centered")

# --- 2. 認証チェック ---
if check_password():

    # --- CSS: デザインの最適化（優しい色合い・ソフトデザイン） ---
    st.markdown("""
        <style>
        /* 全体の背景：目に優しいオフホワイト */
        .stApp { 
            background-color: #fcfbf9; 
        }
        
        /* メインコンテナの幅とパディング */
        .block-container {
            max-width: 800px !important;
            padding-top: 30px !important;
            padding-bottom: 120px !important; 
        }

        /* ログアウトボタンのスタイル（角丸・優しい色） */
        div.stButton > button {
            background-color: #ffffff;
            color: #7d8c9e;
            border: 1px solid #e0e0e0;
            border-radius: 20px;
            font-size: 12px;
            padding: 0.4rem 1rem;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            color: #d9534f; /* ホバー時は淡い赤で警告色 */
            border-color: #d9534f;
            background-color: #fff5f5;
        }

        /* チャット入力欄 */
        [data-testid="stChatInput"] {
            border-radius: 20px !important;
            border: 1px solid #e6e6e6 !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.03) !important;
        }

        /* フッター */
        .custom-copyright-footer {
            position: fixed;
            bottom: 10px;
            left: 0;
            width: 100%;
            text-align: center;
            z-index: 0;
            pointer-events: none;
        }
        .copyright-text {
            color: #b0b0c0;
            font-size: 10px;
            font-family: sans-serif;
        }
        </style>
        
        <div class="custom-copyright-footer">
            <span class="copyright-text">© 2026 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office</span>
        </div>
    """, unsafe_allow_html=True)

    # --- ヘッダーレイアウト (st.columnsを使用) ---
    # ヘッダー全体を囲むコンテナ（白背景・角丸・影付き）
    with st.container():
        st.markdown('<div style="background-color: white; padding: 20px 20px 10px 20px; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.02); margin-bottom: 30px;">', unsafe_allow_html=True)
        
        # カラム比率: [ロゴ(1.5) : タイトル(4.5) : ボタン(1)]
        col1, col2, col3 = st.columns([1.5, 4.5, 1.2])

        # 左カラム：ロゴ画像
        with col1:
            logo_path = "image/CSI&LC IMAIのロゴ.jpg"
            if os.path.exists(logo_path):
                st.image(logo_path, width=80)
            else:
                st.warning("No Image")

        # 中央カラム：事務所名とサブタイトル
        with col2:
            st.markdown("""
                <div style="display: flex; flex-direction: column; justify-content: center; height: 100%; padding-top: 5px;">
                    <span style="font-size: 20px; font-weight: bold; color: #2d4059; line-height: 1.2;">今井久一郎<br>社会保険労務士事務所</span>
                    <span style="font-size: 12px; color: #8899a6; margin-top: 5px;">就業規則・労務リスク判定 AIアシスタント</span>
                </div>
            """, unsafe_allow_html=True)

        # 右カラム：ログアウトボタン
        with col3:
            st.write("") # 上部の余白調整
            if st.button("ログアウト", key="logout_btn"):
                logout()
        
        st.markdown('</div>', unsafe_allow_html=True) # コンテナの閉じタグ


    # --- チャットロジック ---
    
    # セッション状態の初期化
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())

    # 過去のメッセージを表示
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- チャット入力エリア ---
    if prompt := st.chat_input("就業規則の条文を入力してください..."):
        # ユーザー入力を表示＆保存
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AIの回答処理
        with st.chat_message("assistant"):
            # ステータス表示
            with st.status("🌿 解析・判定中...", expanded=True) as status:
                try:
                    D_KEY = st.secrets["DIFY_API_KEY"]
                    
                    response = requests.post(
                        "https://api.dify.ai/v1/chat-messages",
                        headers={
                            "Authorization": f"Bearer {D_KEY}", 
                            "Content-Type": "application/json"
                        },
                        json={
                            "inputs": {}, 
                            "query": prompt, 
                            "response_mode": "blocking", 
                            "user": st.session_state.user_id
                        },
                        timeout=120
                    )
                    
                    response.raise_for_status()
                    res_json = response.json()
                    answer = res_json.get("answer", "")
                    
                    if answer:
                        status.update(label="✨ 判定完了", state="complete", expanded=False)
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else:
                        status.update(label="⚠️ 回答なし", state="error")
                        st.error("AIからの回答が得られませんでした。")
                        
                except Exception as e:
                    status.update(label="❌ エラー発生", state="error")
                    st.error(f"システムエラー: {str(e)}")

    # 画面下部の余白
    st.write("<br><br>", unsafe_allow_html=True)