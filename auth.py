import streamlit as st

def check_password():
    """認証状態をチェックし、洗練されたログイン画面を表示する"""
    
    def password_entered():
        """入力判定"""
        valid_user = st.secrets.get("LOGIN_USER", "imai")
        valid_pw = st.secrets.get("LOGIN_PW", "imai2024")

        if (st.session_state["username"] == valid_user and
            st.session_state["password"] == valid_pw):
            st.session_state["password_correct"] = True
            del st.session_state["password"] 
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    # --- ログイン画面専用のカスタムCSS ---
    st.markdown("""
        <style>
        /* 背景をネイビーのグラデーションに */
        .stApp {
            background: linear-gradient(135deg, #061e3d 0%, #10305a 100%);
        }
        
        /* ログインカードの設定 */
        .login-card {
            background-color: rgba(255, 255, 255, 0.95);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            margin-top: 50px;
        }
        
        /* ロゴの再現 (H IMAI) */
        .login-logo-circle {
            width: 80px; height: 80px;
            background: #061e3d;
            border-radius: 50%;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            margin: 0 auto 20px;
        }
        .login-logo-h { color: #ffffff; font-size: 36px; font-weight: 900; font-family: 'Georgia', serif; line-height: 1; }
        .login-logo-imai { font-size: 10px; font-weight: bold; color: #ffffff; margin-top: -2px; }

        .login-header {
            text-align: center;
            color: #061e3d;
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 30px;
        }
        
        /* 入力フィールドのカスタマイズ */
        div[data-baseweb="input"] {
            border-radius: 10px !important;
        }
        
        /* ボタンのカスタマイズ */
        div.stButton > button {
            background-color: #061e3d;
            color: white;
            border-radius: 10px;
            width: 100%;
            height: 3em;
            font-weight: bold;
            border: none;
            transition: 0.3s;
        }
        div.stButton > button:hover {
            background-color: #c5a059; /* ゴールド */
            color: #061e3d;
        }
        </style>
        
        <div class="login-card">
            <div class="login-logo-circle">
                <span class="login-logo-h">H</span>
                <span class="login-logo-imai">IMAI</span>
            </div>
            <div class="login-header">
                今井社会保険労務士事務所<br>
                <span style="font-size: 14px; font-weight: 400; opacity: 0.8;">Client Portal</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # ログインフォーム
    left, mid, right = st.columns([1, 3, 1])
    with mid:
        with st.form("login_form"):
            st.text_input("ユーザーID", key="username", placeholder="Username")
            st.text_input("パスワード", type="password", key="password", placeholder="Password")
            if st.form_submit_button("ログイン"):
                password_entered()
                if not st.session_state.get("password_correct", False):
                    st.error("認証に失敗しました。")
                else:
                    st.rerun()
                    
    return False

def logout():
    """ログアウト処理"""
    if st.sidebar.button("Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()