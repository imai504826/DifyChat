import streamlit as st

def check_password():
    """
    ユーザー認証を行い、認証済みであればTrueを返す。
    Username / Password の表記とキーを完全に一致させています。
    """

    # --- 1. デザイン定義 (CSS) ---
    st.markdown("""
        <style>
        .stApp { background-color: #f9f9fb !important; }
        .main .block-container {
            max-width: 480px !important;
            padding-top: 4rem !important;
            padding-bottom: 120px !important;
        }
        .login-header-card {
            background-color: #ffffff;
            padding: 25px 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border: 1px solid #eaeaea;
            margin-bottom: 30px;
        }
        .fixed-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #ffffff;
            border-top: 1px solid #eaeaea;
            padding: 15px 0;
            text-align: center;
            z-index: 9999;
        }
        .footer-notice { color: #d93025; font-size: 11px; font-weight: bold; display: block; margin-bottom: 4px; }
        .footer-copy { color: #888888; font-size: 10px; display: block; }
        div.stButton > button {
            width: 100%;
            background-color: #061e3d !important;
            color: white !important;
            border: none;
            padding: 12px;
            font-weight: bold;
            margin-top: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- 2. 認証ロジック ---
    def password_entered():
        # Secretsの中に [passwords] グループがあるか確認
        if "passwords" not in st.secrets:
            st.error("Secrets設定に [passwords] が見つかりません。")
            return

        # フォームの key="username" と key="password" から値を取得
        user_input = st.session_state.get("username")
        pass_input = st.session_state.get("password")

        # 照合
        if user_input in st.secrets["passwords"] and pass_input == st.secrets["passwords"][user_input]:
            st.session_state["password_correct"] = True
            # セキュリティのため入力をクリア
            if "password" in st.session_state: del st.session_state["password"]
            if "username" in st.session_state: del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # 既にログイン済みの判定
    if st.session_state.get("password_correct", False):
        return True

    # --- 3. ログイン画面の表示 ---
    
    # ヘッダーカード
    st.markdown("""
        <div class="login-header-card">
            <div style="display: flex; align-items: center;">
                <div style="width: 50px; height: 50px; background-color: #061e3d; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-right: 15px;">
                    <span style="color: #ffffff; font-size: 22px; font-weight: 900; line-height: 1;">H</span>
                    <span style="font-size: 8px; font-weight: bold; color: #ffffff; margin-top: -2px;">IMAI</span>
                </div>
                <div>
                    <div style="color: #061e3d; font-size: 18px; font-weight: 700; line-height: 1.2;">今井久一郎 社会保険労務士事務所</div>
                    <div style="color: #666666; font-size: 12px; margin-top: 2px;">就業規則・労務リスク判定 AIアシスタント</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 入力フォーム（指示通りの key 設定）
    st.write("### ログイン")
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
    if st.sidebar.button("Logout"):
        st.session_state["password_correct"] = False
        st.rerun()