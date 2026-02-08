import streamlit as st
import requests
import uuid
from auth import check_password, logout

# --- 1. ページ設定 ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="⚖️", layout="centered")

# --- 2. 認証チェック ---
if check_password():
    
    # --- CSS: シンプルな構造に整理 ---
    st.markdown("""
        <style>
        /* 全体背景とコンテンツ幅 */
        .stApp { background-color: #f9f9fb; }
        .block-container {
            max-width: 730px !important;
            padding-bottom: 120px !important; /* フッター分の余白 */
        }

        /* 1. 入力エリアの背景（白い帯）を標準コンテナに密着させる */
        [data-testid="stChatFloatingInputContainer"] {
            background-color: #ffffff !important;
            border-top: 1px solid #eaeaea !important;
            padding: 20px 0 40px 0 !important; /* 下部にCopyRight用の隙間を作る */
            left: 0 !important;
            right: 0 !important;
        }

        /* 2. 入力ボックス自体のデザインを整え、変な枠を消す */
        [data-testid="stChatInput"] {
            max-width: 690px !important; /* 730pxの内側に収める */
            margin: 0 auto !important;
            border: 1px solid #e0e0e0 !important;
            border-radius: 8px !important;
        }
        
        /* 入力ボックス内部の余計な影や枠をリセット */
        [data-testid="stChatInput"] > div {
            border: none !important;
            box-shadow: none !important;
        }

        /* 3. CopyRightエリア：入力コンテナの中に配置して絶対にズレないようにする */
        .custom-footer {
            position: absolute;
            bottom: 8px; /* 入力エリアのすぐ下 */
            left: 0;
            right: 0;
            text-align: center;
            pointer-events: none;
            line-height: 1.4;
        }

        .notice-red {
            color: #d93025;
            font-size: 10.5px;
            font-weight: 700;
            display: block;
        }
        .copyright-gray {
            color: #888888;
            font-size: 9px;
            display: block;
        }
        </style>
        """, unsafe_allow_html=True)

    # --- ヘッダー（幅固定） ---
    st.markdown("""
        <div style="background-color: #ffffff; padding: 25px 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #eaeaea; margin-bottom: 30px; max-width: 730px; margin-left: auto; margin-right: auto;">
            <div style="display: flex; align-items: center;">
                <div style="width: 58px; height: 58px; background-color: #061e3d; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-right: 20px; flex-shrink: 0;">
                    <span style="color: #ffffff; font-size: 26px; font-weight: 900; line-height: 1;">H</span>
                    <span style="font-size: 9px; font-weight: bold; color: #ffffff; margin-top: -2px;">IMAI</span>
                </div>
                <div>
                    <div style="color: #061e3d; font-size: 21px; font-weight: 700; line-height: 1.2;">今井社会保険労務士事務所</div>
                    <div style="color: #666666; font-size: 13.5px; margin-top: 2px;">就業規則・労務リスク判定 AIアシスタント</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        logout()

    # チャット履歴の表示
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- 4. チャット入力とフッターの連動 ---
    # st.chat_input は常に表示される
    if prompt := st.chat_input("就業規則の条文を入力してください..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.status("🔍 解析・判定中...", expanded=True) as status:
                try:
                    D_KEY = st.secrets["DIFY_API_KEY"]
                    response = requests.post(
                        "https://api.dify.ai/v1/chat-messages",
                        headers={"Authorization": f"Bearer {D_KEY}", "Content-Type": "application/json"},
                        json={"inputs": {}, "query": prompt, "response_mode": "blocking", "user": st.session_state.user_id},
                        timeout=120
                    )
                    response.raise_for_status()
                    answer = response.json().get("answer", "回答を取得できませんでした。")
                    status.update(label="✅ 判定完了", state="complete", expanded=False)
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    status.update(label="❌ エラー", state="error")
                    st.error(f"システムエラーが発生しました。")

    # --- 5. CopyRightを「入力エリアコンテナ」の中に差し込む ---
    # HTMLの配置場所を変えることで、サイドバーとのズレを物理的に解消
    st.markdown("""
        <script>
        const observer = new MutationObserver(function(mutations) {
            const inputContainer = document.querySelector('[data-testid="stChatFloatingInputContainer"]');
            if (inputContainer && !document.querySelector('.custom-footer')) {
                const footer = document.createElement('div');
                footer.className = 'custom-footer';
                footer.innerHTML = `
                    <span class="copyright-gray">© 2026 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office</span>
                `;
                inputContainer.appendChild(footer);
            }
        });
        observer.observe(document.body, {childList: true, subtree: true});
        </script>
    """, unsafe_allow_html=True)