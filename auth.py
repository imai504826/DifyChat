import streamlit as st

def check_password():
    """ユーザー名とパスワードを確認し、認証状態を管理する関数"""
    
    def password_entered():
        """入力された内容を判定する内部関数"""
        # Secretsから取得、未設定ならデフォルト値(imai / imai2024)を使用
        valid_user = st.secrets.get("LOGIN_USER", "imai")
        valid_pw = st.secrets.get("LOGIN_PW", "imai2024")

        if (st.session_state["username"] == valid_user and
            st.session_state["password"] == valid_pw):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # セキュリティのため削除
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # すでにログイン済みならTrueを返す
    if st.session_state.get("password_correct", False):
        return True

    # ログイン画面の表示
    st.markdown("<h2 style='text-align: center; color: #061e3d;'>Client Login</h2>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        if st.form_submit_button("Login"):
            password_entered()
            if not st.session_state.get("password_correct", False):
                st.error("😕 ユーザー名またはパスワードが正しくありません")
            else:
                st.rerun()
    
    return False

def logout():
    """ログアウト処理を行う関数"""
    if st.sidebar.button("Logout"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()