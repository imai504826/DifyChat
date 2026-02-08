import streamlit as st

def check_password():
    """
    ユーザー認証を行い、認証済みであればTrueを返す。
    デザインとログインロジックを分離して整理。
    """

    # --- 1. ログイン画面専用のデザイン（CSS） ---
    # 画面最下部に固定されるフッターと、入力フォームのスタイルを定義
    st.markdown("""
        <style>
        /* ログイン画面全体の背景色 */
        .stApp {
            background-color: #f9f9fb !important;
        }

        /* ログインフォームがあるメインエリアの余白調整 */
        .main .block-container {
            max-width: 450px !important; /* ログインフォームを中央に寄せて見やすく */
            padding-top: 5rem !important;
            padding-bottom: 120px !important;
        }

        /* --- 下部固定フッターのデザイン --- */
        .login-footer {
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

        .footer-notice {
            color: #d93025;
            font-size: 11px;
            font-weight: bold;
            margin-bottom: 5px;
            display: block;
            padding: 0 20px;
        }

        .footer-copy {
            color: #888888;
            font-size: 10px;
            display: block;
        }
        
        /* ボタンなどのUI微調整 */
        div.stButton > button {
            width: 100%;
            background-color: #061e3d;
            color: white;
            border-radius: 5px;
        }
        </style>

        <div class="login-footer">
            <span class="footer-notice">【免責事項】本AIの回答は法的助言ではありません。最終判断は必ず専門家へ相談の上、自己責任で行ってください。</span>
            <span class="footer-copy">© 2026 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office</span>
        </div>
    """, unsafe_allow_html=True)

    def password_entered():
        """入力されたパスワードが正しいかチェックする関数"""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"] == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # セキュリティのためパスワードを削除
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # すでに認証済みの場合はTrueを返す
    if st.session_state.get("password_correct", False):
        return True

    # --- 2. ログインフォームの表示 ---
    st.write("## ⚖️ 労務リスク判定 AI")
    st.write("ご利用にはログインが必要です。")
    
    st.text_input("ユーザー名", key="username")
    st.text_input("パスワード", type="password", key="password", on_change=password_entered)
    
    if st.button("ログイン"):
        password_entered()
        if not st.session_state.get("password_correct", False):
            st.error("⚠️ ユーザー名またはパスワードが正しくありません。")
            return False
        else:
            st.rerun()
            return True

    return False

def logout():
    """ログアウト処理"""
    if st.button("ログアウト"):
        st.session_state["password_correct"] = False
        st.rerun()