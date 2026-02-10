import streamlit as st
import os
import base64

def get_image_base64(file_path):
    """画像をBase64文字列に変換する"""
    if os.path.exists(file_path):
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

def check_password():
    """
    ユーザー認証を行い、認証済みであればTrueを返す。
    """

    # --- 1. デザイン定義 (CSS: 優しい色合い) ---
    st.markdown("""
        <style>
        /* 背景色をウォームホワイトに */
        .stApp { background-color: #fcfbf9 !important; }
        
        .main .block-container {
            max-width: 450px !important;
            padding-top: 5rem !important;
        }
        
        /* ログインカードのデザインを柔らかく */
        .login-header-card {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 10px 25px rgba(200, 210, 220, 0.2);
            border: 1px solid #f2f2f2;
            margin-bottom: 25px;
            text-align: center;
        }

        /* 入力ラベルの調整 */
        .stTextInput label {
            color: #7f8c8d !important;
        }

        /* ログインボタンを優しい色に */
        div.stButton > button {
            width: 100%;
            background-color: #5d6d7e !important; /* 柔らかいスレートグレー */
            color: white !important;
            border: none;
            border-radius: 10px;
            padding: 10px;
            font-weight: bold;
            margin-top: 20px;
            transition: 0.3s;
        }
        div.stButton > button:hover {
            background-color: #485461 !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }

        /* フッター */
        .fixed-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: rgba(252, 251, 249, 0.9);
            padding: 15px 0;
            text-align: center;
            z-index: 9999;
        }
        .footer-notice { color: #c0392b; font-size: 10px; display: block; margin-bottom: 4px; padding: 0 20px; }
        .footer-copy { color: #aab; font-size: 9px; display: block; }
        </style>
    """, unsafe_allow_html=True)

    # --- 2. 認証ロジック ---
    def password_entered():
        if "passwords" not in st.secrets:
            st.error("Secrets設定に [passwords] が見つかりません。")
            return

        user_input = st.session_state.get("username")
        pass_input = st.session_state.get("password")

        if user_input in st.secrets["passwords"] and pass_input == st.secrets["passwords"][user_input]:
            st.session_state["password_correct"] = True
            if "password" in st.session_state: del st.session_state["password"]
            if "username" in st.session_state: del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # 既にログイン済みの判定
    if st.session_state.get("password_correct", False):
        return True

    # --- 3. ログイン画面の表示 ---
    
    # ロゴの読み込み
    logo_path = "image/CSI&LC IMAIのロゴ.jpg"
    logo_b64 = get_image_base64(logo_path)

    # ヘッダーカード（ロゴ＋タイトル）
    if logo_b64:
        logo_html = f'<img src="data:image/jpeg;base64,{logo_b64}" style="width: 80px; margin-bottom: 15px;">'
    else:
        logo_html = '<div style="font-size: 40px; margin-bottom: 10px;">⚖️</div>'

    st.markdown(f"""
        <div class="login-header-card">
            {logo_html}
            <div style="color: #2c3e50; font-size: 19px; font-weight: 700; line-height: 1.4;">
                今井久一郎<br>社会保険労務士事務所
            </div>
            <div style="color: #95a5a6; font-size: 12px; margin-top: 8px;">
                労務リスク判定 AIアシスタント
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 入力フォーム
    with st.container():
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password", on_change=password_entered)
        
        if st.button("Sign In"):
            password_entered()
            if not st.session_state.get("password_correct", False):
                st.error("⚠️ ユーザー名またはパスワードが正しくありません。")

    # フッター
    st.markdown("""
        <div class="fixed-footer">
            <span class="footer-notice">【免責事項】本AIの回答は法的助言ではありません。最終判断は必ず専門家へ相談の上、自己責任で行ってください。</span>
            <span class="footer-copy">© 2026 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office</span>
        </div>
    """, unsafe_allow_html=True)

    return False

def logout():
    """
    ログアウト処理: セッションをクリアしてリライト
    app.py側で st.button が押された時に呼び出されます。
    """
    st.session_state["password_correct"] = False
    # チャット履歴等も消去
    if "messages" in st.session_state:
        st.session_state["messages"] = []
    # ログイン画面に強制的に戻すためにリライトを実行
    st.rerun()