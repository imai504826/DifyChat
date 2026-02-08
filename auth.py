import streamlit as st

def check_password():
    """認証状態をチェックし、未ログインならログイン画面を表示する"""
    
    def password_entered():
        """入力判定"""
        # Secretsから取得（未設定時のデフォルト: imai / imai2024）
        valid_user = st.secrets.get("LOGIN_USER", "imai")
        valid_pw = st.secrets.get("LOGIN_PW", "imai504826")

        if (st.session_state["username"] == valid_user and
            st.session_state["password"] == valid_pw):
            st.session_state["password_correct"] = True
            del st.session_state["password"] 
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # 1. すでにログイン済みの場合
    if st.session_state.get("password_correct", False):
        return True

    # 2. 未ログインの場合（ログイン画面を表示）
    st.markdown("<h2 style='text-align: center; color: #061e3d; margin-top: 50px;'>Client Login</h2>", unsafe_allow_html=True)
    
    with st.container():
        left, mid, right = st.columns([1, 2, 1])
        with mid:
            with st.form("login_form"):
                st.text_input("Username", key="username")
                st.text_input("Password", type="password", key="password")
                if st.form_submit_button("Login", use_container_width=True):
                    password_entered()
                    if not st.session_state.get("password_correct", False):
                        st.error("😕 ユーザー名またはパスワードが違います")
                    else:
                        st.rerun()
    return False

def logout():
    """ログアウト処理"""
    if st.sidebar.button("Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()