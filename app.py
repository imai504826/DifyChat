import streamlit as st
import requests
import uuid
from auth import check_password, logout

# --- 1. ページ設定 (最上部に配置) ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="⚖️", layout="centered")

# --- 2. 認証チェック ---
if check_password():
    
    # --- デザインCSS（余計な空白を徹底排除） ---
    st.markdown("""
        <style>
        /* 1. Streamlit標準の上部空白と余計な要素を消す */
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stAppDeployButton {display:none;}
        
        .block-container {
            padding-top: 1rem !important; /* 上の余白を最小化 */
            max-width: 700px;
        }

        /* 2. 背景とカードの設定 */
        .stApp { background-color: #f9f9fb; }
        
        .main-card {
            background-color: #ffffff;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border: 1px solid #eaeaea;
            margin-top: 0px;
        }
        
        /* 3. ヘッダー（画像に合わせて最適化） */
        .header-container {
            display: flex;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f2f6;
            margin-bottom: 20px;
        }
        
        .logo-box {
            width: 55px; height: 55px;
            background-color: #061e3d;
            border-radius: 50%;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            margin-right: 15px; flex-shrink: 0;
        }
        .logo-h { color: #ffffff; font-size: 26px; font-weight: 900; font-family: 'Georgia', serif; line-height: 1; }
        .logo-imai { font-size: 8px; font-weight: bold; color: #ffffff; margin-top: -2px; }

        .header-title { color: #061e3d; font-size: 20px; font-weight: 700; margin: 0; }
        .header-subtitle { color: #666666; font-size: 12px; margin-top: 2px; }
        
        /* 4. 免責事項（確実に見えるデザイン） */
        .disclaimer-box {
            background-color: #f8f9fa;
            border-left: 5px solid #061e3d;
            padding: 15px;
            margin: 10px 0 20px 0;
            border-radius: 4px;
        }
        .disclaimer-text {
            color: #444444; font-size: 11px; line-height: 1.6; margin: 0;
        }

        /* 5. フッター */
        .custom-footer {
            margin-top: 30px; color: #888888; text-align: center;
            font-size: 10px; padding-bottom: 20px;
        }
        </style>
        """, unsafe_allow_html=True)

    # --- 重要事項（免責）表示関数 ---
    def display_disclaimer():
        st.markdown("""
            <div class="disclaimer-box">
                <p class="disclaimer-text">
                    <strong>【AI判定に関する重要事項】</strong><br>
                    本システムは、当事務所が監修した<strong>最新の就業規則ナレッジ（RAG）を直接参照</strong>しており、一般的なAIに比べ高い正確性を備えています。<br>
                    しかしながら、本回答はAIによる推論であり法的助言を確定させるものではありません。個別の事案に対する最終的な判断については、必ず当事務所の社会保険労務士にご確認ください。
                </p>
            </div>
        """, unsafe_allow_html=True)

    # --- メインコンテンツ ---
    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    # ヘッダー（最上部に直置き）
    st.markdown("""
        <div class="header-container">
            <div class="logo-box"><span class="logo-h">H</span><span class="logo-imai">IMAI</span></div>
            <div>
                <div class="header-title">今井社会保険労務士事務所</div>
                <div class="header-subtitle">就業規則・労務リスク判定 AIアシスタント</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ログアウトボタン（サイドバーへ移動してメイン画面をスッキリさせる）
    with st.sidebar:
        logout()

    # --- Dify 連携ロジック ---
    try:
        D_KEY = st.secrets["DIFY_API_KEY"]
    except:
        st.error("APIキー未設定")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())

    # 履歴表示（ここでも免責を確実に出す）
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
        if msg["role"] == "assistant":
            display_disclaimer()

    # 入力エリア
    if prompt := st.chat_input("就業規則の条文を入力してください..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            res_box = st.empty()
            res_box.markdown("🔍 判定中...")
            try:
                response = requests.post(
                    "https://api.dify.ai/v1/chat-messages",
                    headers={"Authorization": f"Bearer {D_KEY}", "Content-Type": "application/json"},
                    json={"inputs": {}, "query": prompt, "response_mode": "blocking", "user": st.session_state.user_id},
                    timeout=60
                )
                answer = response.json().get("answer", "回答不可")
                res_box.markdown(answer)
                display_disclaimer() # 回答直後に表示
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="custom-footer">© 2024 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office</div>', unsafe_allow_html=True)