import streamlit as st
import requests
import uuid
from auth import check_password, logout

# --- 1. ページ設定 ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="⚖️", layout="centered")

# --- 2. 認証チェック ---
if check_password():
    
    # --- CSS: デザインの最適化 ---
    st.markdown("""
        <style>
        .stApp { background-color: #f9f9fb; }
        .block-container {
            max-width: 730px !important;
            padding-bottom: 160px !important; 
        }
        [data-testid="stChatFloatingInputContainer"] {
            background-color: #ffffff !important;
            border-top: 1px solid #eaeaea !important;
            padding: 20px 0 60px 0 !important;
            left: 0 !important;
            right: 0 !important;
            z-index: 99 !important;
        }
        [data-testid="stChatInput"] {
            max-width: 690px !important;
            margin: 0 auto !important;
            border: 1px solid #e0e0e0 !important;
            border-radius: 8px !important;
            background-color: #fcfcfc !important;
        }
        .custom-copyright-footer {
            position: fixed;
            bottom: 20px;
            left: 0;
            right: 0;
            width: 100%;
            text-align: center;
            z-index: 100;
            pointer-events: none;
        }
        .copyright-text {
            color: #888888;
            font-size: 10px;
            font-family: sans-serif;
            max-width: 730px;
            margin: 0 auto;
            display: block;
        }
        </style>
        
        <div class="custom-copyright-footer">
            <span class="copyright-text">© 2026 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office</span>
        </div>
        """, unsafe_allow_html=True)

    # --- ヘッダー ---
    st.markdown("""
        <div style="background-color: #ffffff; padding: 25px 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #eaeaea; margin-bottom: 30px; max-width: 730px; margin-left: auto; margin-right: auto;">
            <div style="display: flex; align-items: center;">
                <div style="width: 58px; height: 58px; background-color: #061e3d; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-right: 20px; flex-shrink: 0;">
                    <span style="color: #ffffff; font-size: 26px; font-weight: 900; line-height: 1;">H</span>
                    <span style="font-size: 9px; font-weight: bold; color: #ffffff; margin-top: -2px;">IMAI</span>
                </div>
                <div>
                    <div style="color: #061e3d; font-size: 21px; font-weight: 700; line-height: 1.2;">今井久一郎 社会保険労務士事務所</div>
                    <div style="color: #666666; font-size: 13.5px; margin-top: 2px;">就業規則・労務リスク判定 AIアシスタント</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        logout()

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
            with st.status("🔍 解析・判定中...", expanded=True) as status:
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
                    
                    # HTTPエラーのチェック
                    response.raise_for_status()
                    res_json = response.json()
                    
                    # 回答の抽出
                    answer = res_json.get("answer", "")
                    
                    if answer:
                        # 正常終了
                        status.update(label="✅ 判定完了", state="complete", expanded=False)
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else:
                        # APIは成功したが、中身がない場合
                        status.update(label="⚠️ 回答が得られませんでした", state="error")
                        st.error("Difyから有効な回答が返されませんでした。API設定を確認してください。")
                        
                except Exception as e:
                    # エラー原因を画面に表示（デバッグ用）
                    status.update(label="❌ システムエラー", state="error")
                    st.error(f"システムエラーが発生しました: {str(e)}")

    # 画面下部の余白確保
    st.write("<br><br>", unsafe_allow_html=True)