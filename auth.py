import streamlit as st

def check_password():
    """
    ユーザー認証を行い、認証済みであればTrueを返す。
    ヘッダー：今井久一郎 社会保険労務士事務所
    フッター：免責事項 ＋ CopyRight を最下部に固定
    """

    # --- 1. CSSスタイル定義 (デザインの全集約) ---
    st.markdown("""
        <style>
        /* 背景色と全体のフォント設定 */
        .stApp { background-color: #f9f9fb !important; }

        /* ログインフォームを中央に配置し、読みやすくする */
        .main .block-container {
            max-width: 460px !important;
            padding-top: 4rem !important;
            padding-bottom: 120px !important; /* フッターと被らないための余白 */
        }

        /* ヘッダーカード：以前のプロ仕様デザインを再現 */
        .login-header-card {
            background-color: #ffffff;
            padding: 25px 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border: 1px solid #eaeaea;
            margin-bottom: 35px;
        }

        /* --- 固定フッター (免責事項 ＋ コピーライト) --- */
        .fixed-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #ffffff;
            border-top: 1px solid #eaeaea;
            padding: 18px 0;
            text-align: center;
            z-index: 9999;
        }

        .footer-notice {
            color: #d93025;
            font-size: 11px;
            font-weight: bold;
            display: block;
            margin-bottom: 6px;
            padding: 0 20px;
            line-height: 1.4;
        }

        .footer-copy {
            color: #888888;
            font-size: 10px;
            display: block;
            letter-spacing: 0.5px;
        }

        /* 入力ラベルとボタンの装飾 */
        label { font-weight: 600 !important; color: #444 !important; }
        
        div.stButton > button {
            width: 100%;
            background-color: #061e3d !important;
            color: white !important;
            border: none;
            padding: 10px;
            font-weight: bold;
            margin-top: 15px;
            transition: 0.3s;
        }
        div.stButton > button:hover {
            opacity: 0.9;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- 2. ログイン判定ロジック ---
    def password_entered():
        """認証チェック用コールバック"""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"] == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # セキュリティのため削除
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # 既に認証済みの場合はメイン画面へ
    if st.session_state.get("password_correct", False):
        return True

    # --- 3. 画面表示レイアウト ---
    
    # 今井久一郎デザインのヘッダーカード
    st.markdown("""
        <div class="login-header-card">
            <div style="display: flex; align-items: center;">
                <div style="width: 50px; height: 50px; background-color: #061e3d; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-right: 18px;">
                    <span style="color: #ffffff; font-size: 22px; font-weight: 900; line-height: 1;">H</span>
                    <span style="font-size: 8px; font-weight: bold; color: #ffffff; margin-top: -2px;">IMAI</span>
                </div>
                <div>
                    <div style="color: #061e3d; font-size: 18px; font-weight: 700; line-height: 1.2;">今井久一郎 社会保険労務士事務所</div>
                    <div style="color: #666666; font-size: 11.5px; margin-top: 3px;">就業規則・労務リスク判定 AIアシスタント PORTAL</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ログインフォーム本体
    st.write("### ログイン")
    st.text_input("Username", key="username", placeholder="ユーザー名を入力")
    st.text_input("Password", type="password", key="password", placeholder="パスワードを入力", on_change=password_entered)
    
    if st.button("Sign In"):
        password_entered()
        if not st.session_state.get("password_correct", False):
            st.error("⚠️ ユーザー名またはパスワードが正しくありません。")

    # フッター (免責事項 ＋ コピーライト)
    st.markdown("""
        <div class="fixed-footer">
            <span class="footer-notice">【免責事項】本AIの回答は法的助言ではありません。最終判断は必ず専門家へ相談の上、自己責任で行ってください。</span>
            <span class="footer-copy">© 2026 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office</span>
        </div>
    """, unsafe_allow_html=True)

    return False

def logout():
    """サイドバー用ログアウト関数"""
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state["password_correct"] = False
        st.rerun()