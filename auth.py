import streamlit as st

def check_password():
    """白を基調としたシンプルで洗練されたログイン画面を表示する"""
    def password_entered():
        """入力判定"""
        valid_user = st.secrets.get("LOGIN_USER", "imai")
        valid_pw = st.secrets.get("LOGIN_PW", "imai504826")

        if (st.session_state["username"] == valid_user and
            st.session_state["password"] == valid_pw):
            st.session_state["password_correct"] = True
            del st.session_state["password"] 
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    # --- ログイン画面専用のカスタムCSS (白ベース) ---
    st.markdown("""
        <style>
        /* 背景を明るいグレー/白に設定 */
        .stApp {
            background-color: #f8f9fa;
        }
        
        /* ログインコンテナの装飾 */
        .login-wrapper {
            max-width: 400px;
            margin: 80px auto 20px auto;
            padding: 40px;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.05);
            text-align: center;
            border: 1px solid #eaeaea;
        }
        
        /* ロゴのデザイン (H IMAI) */
        .logo-circle-small {
            width: 65px; height: 65px;
            background: #061e3d;
            border-radius: 50%;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            margin: 0 auto 20px;
        }
        .logo-h-small { color: #ffffff; font-size: 30px; font-weight: 900; font-family: 'Georgia', serif; line-height: 1; }
        .logo-imai-small { font-size: 8px; font-weight: bold; color: #ffffff; margin-top: -2px; }

        .office-name {
            color: #061e3d;
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        .portal-label {
            color: #888888;
            font-size: 12px;
            margin-bottom: 30px;
            letter-spacing: 1px;
        }
        
        /* Streamlitのフォーム境界線を消してスッキリさせる */
        [data-testid="stForm"] {
            border: none !important;
            padding: 0 !important;
        }
        
        /* ボタンをネイビーに */
        div.stButton > button {
            background-color: #061e3d;
            color: white;
            border-radius: 8px;
            width: 100%;
            border: none;
            padding: 10px;
            font-weight: 600;
        }
        div.stButton > button:hover {
            background-color: #10305a;
            color: white;
        }
        </style>
        
        <div class="login-wrapper">
            <div class="logo-circle-small">
                <span class="logo-h-small">H</span>
                <span class="logo-imai-small">IMAI</span>
            </div>
            <div class="office-name">今井久一郎 社会保険労務士事務所</div>
            <div class="portal-label">就業規則・労務リスク判定 AIアシスタント PORTAL</div>
        </div>
    """, unsafe_allow_html=True)
    
    # 入力フォーム
    left, mid, right = st.columns([1, 2, 1])
    with mid:
        with st.form("login_form"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            if st.form_submit_button("Sign In"):
                password_entered()
                if not st.session_state.get("password_correct", False):
                    st.error("Invalid credentials")
                else:
                    st.rerun()
                    
    return False

def logout():
    """ログアウト処理"""
    if st.sidebar.button("Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()