import streamlit as st
import requests
import uuid
import base64
import os
from auth import check_password, logout

# --- 1. ページ設定 ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="🌿", layout="centered")

# --- 画像読み込み関数 ---
def get_image_base64(file_path):
    """画像をBase64文字列に変換する"""
    if os.path.exists(file_path):
        with open(file_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode()
            return f"data:image/jpeg;base64,{encoded_string}" # 拡張子がpngなら image/png に変更
    return None

# --- 2. 認証チェック ---
if check_password():

    # --- CSS: デザインの最適化（優しい色合い・ソフトデザイン） ---
    st.markdown("""
        <style>
        /* 全体の背景：目に優しいオフホワイト */
        .stApp { 
            background-color: #fcfbf9; 
        }
        
        /* メインコンテナの幅調整 */
        .block-container {
            max-width: 730px !important;
            padding-bottom: 160px !important; 
        }
        
        /* チャット入力欄のデザイン */
        [data-testid="stChatFloatingInputContainer"] {
            background-color: transparent !important;
            padding-bottom: 20px !important;
        }
        [data-testid="stChatInput"] {
            background-color: #ffffff !important;
            border: 1px solid #e0e0e0 !important;
            border-radius: 15px !important; /* 角を丸く */
            box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important; /* ふんわりした影 */
        }
        
        /* チャットメッセージのスタイル（オプション） */
        .stChatMessage {
            background-color: transparent;
        }

        /* コピーライトフッター */
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
            color: #aab; /* 淡いグレーパープル */
            font-size: 10px;
            font-family: sans-serif;
        }
        </style>
        
        <div class="custom-copyright-footer">
            <span class="copyright-text">© 2026 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office</span>
        </div>
        """, unsafe_allow_html=True)

    # --- ヘッダー画像の読み込み ---
    # フォルダ構成に合わせてパスを指定
    logo_path = "image/CSI&LC IMAIのロゴ.jpg" 
    logo_src = get_image_base64(logo_path)

    # 画像が見つからない場合のプレースホルダー（念のため）
    if not logo_src:
        logo_html = """
        <div style="width: 70px; height: 70px; background-color: #eee; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 20px;">
            <span style="font-size: 10px; color: #888;">No Image</span>
        </div>
        """
    else:
        logo_html = f'<img src="{logo_src}" style="width: 80px; height: auto; margin-right: 25px; border-radius: 4px;">'

    # --- ヘッダー表示エリア ---
    st.markdown(f"""
        <div style="
            background-color: #ffffff; 
            padding: 30px 40px; 
            border-radius: 20px; 
            box-shadow: 0 10px 25px rgba(200, 210, 220, 0.2); /* 非常に柔らかい影 */
            margin-bottom: 40px; 
            max-width: 730px; 
            margin-left: auto; 
            margin-right: auto;
            border: 1px solid #f2f2f2;
        ">
            <div style="display: flex; align-items: center;">
                {logo_html}
                
                <div>
                    <div style="
                        color: #2c3e50; /* 濃いグレーネイビーで視認性を確保しつつ優しく */
                        font-size: 22px; 
                        font-weight: 700; 
                        line-height: 1.3; 
                        font-family: 'Helvetica Neue', Arial, sans-serif;
                    ">
                        今井久一郎 社会保険労務士事務所
                    </div>
                    <div style="
                        color: #7f8c8d; /* アッシュグレー */
                        font-size: 14px; 
                        margin-top: 5px;
                        font-weight: 400;
                    ">
                        就業規則・労務リスク判定 AIアシスタント
                    </div>
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
            # ステータス表示もデザインに合わせてシンプルに
            with st.status("🍃 解析・判定中...", expanded=True) as status:
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