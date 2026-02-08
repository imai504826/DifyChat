import streamlit as st

def check_password():
    """
    ユーザー認証を行い、認証済みであればTrueを返す。
    エラー回避のため secrets のキー存在確認を強化。
    """

    # --- 1. スタイル定義 (CSS) ---
    st.markdown("""
        <style>
        .stApp { background-color: #f9f9fb !important; }
        .main .block-container {
            max-width: 480px !important;
            padding-top: 4rem !important;
            padding-bottom: 120px !important;
        }
        /* ヘッダーカード */
        .login-header-card {
            background-color: #ffffff;
            padding: 25px 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border: 1px solid #eaeaea;
            margin-bottom: 30px;
        }
        /* 固定フッター */
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
        .footer-notice {
            color: #d93025;
            font-size: 11px;
            font-weight: bold;
            display: block;
            margin-bottom: 4px;
        }
        .footer-copy {
            color: #888888;
            font-size: 10px;
            display: block;
        }
        /* ボタン */
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

    def password_entered():
        """入力チェック (KeyError対策済み)"""
        # secretsの中に 'passwords' があるか確認
        if "passwords" not in st.secrets:
            st.error("設定ファイルに 'passwords' が見つかりません。")
            return

        user = st.session_state.get("username")
        pwd = st.session_state.get("password")

        # ユーザー名が登録されており、パスワードが一致するか
        if user in st.secrets["passwords"] and pwd == st.secrets["passwords"][user]:
            st.session_state["password_correct"] = True
            if "password" in st.session_state: del st.session_state["password"]
            if "username" in st.session_state: del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    # --- 3. 画面描画 ---
    
    # 今井久一郎デザインのヘッダー
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