import streamlit as st

def check_password():
    # --- (中略: パスワードチェックのロジック) ---

    if "password_correct" not in st.session_state:
        # ログイン画面専用のCSSとフッター
        st.markdown("""
            <style>
            /* ログイン画面の背景調整 */
            .stApp { background-color: #f9f9fb; }

            /* ログインフォームの下に余白を作る */
            .main .block-container {
                padding-bottom: 100px !important;
            }

            /* ログイン画面専用フッター */
            .login-footer {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                width: 100%;
                height: 80px;
                background-color: #ffffff;
                border-top: 1px solid #eaeaea;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                z-index: 999;
                pointer-events: none;
            }

            .footer-notice {
                color: #d93025;
                font-size: 10px;
                font-weight: 700;
                margin-bottom: 4px;
                text-align: center;
                padding: 0 20px;
            }

            .footer-copy {
                color: #888888;
                font-size: 9px;
            }
            </style>

            <div class="login-footer">
                <div class="footer-notice">
                    【免責事項】本AIの回答は法的助言ではありません。最終判断は必ず専門家へ相談の上、自己責任で行ってください。
                </div>
                <div class="footer-copy">
                    © 2026 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office
                </div>
            </div>
        """, unsafe_allow_html=True)

        # ここから下の st.text_input などがログインフォーム
        st.write("### ログイン")
        # --- (以下、パスワード入力フォームが続く) ---