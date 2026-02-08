import streamlit as st
import requests
import uuid
from auth import check_password, logout

# --- 1. ページ設定 ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="⚖️", layout="centered")

# --- 2. 認証チェック ---
if check_password():
    
    # --- デザインCSS（空白を徹底的に殺す設定） ---
    st.markdown("""
        <style>
        /* ページ全体の余白調整 */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 3rem !important;
            max-width: 750px;
        }

        /* 画面背景 */
        .stApp { background-color: #f9f9fb; }
        
        /* タイトルエリアのコンテナ（白いカード風） */
        .custom-header-card {
            background-color: #ffffff;
            padding: 25px 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            border: 1px solid #eaeaea;
            margin-bottom: 20px;
        }
        
        /* ロゴと事務所名の並び */
        .header-flex {
            display: flex;
            align-items: center;
        }
        
        .logo-box {
            width: 55px; height: 55px;
            background-color: #061e3d;
            border-radius: 50%;
            display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            margin-right: 20px; flex-shrink: 0;
        }
        .logo-h { color: #ffffff; font-size: 26px; font-weight: 900; font-family: 'Georgia', serif; line-height: 1; }
        .logo-imai { font-size: 8px; font-weight: bold; color: #ffffff; margin-top: -2px; }

        .header-title { color: #061e3d; font-size: 22px; font-weight: 700; margin: 0; }
        .header-subtitle { color: #666666; font-size: 13px; margin-top: 4px; }
        
        /* 重要事項（免責）のデザイン */
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

        /* 履歴部分の白い背景（カード感を出す） */
        .stChatMessage {
            background-color: #ffffff !important;
            border: 1px solid #eaeaea !important;
            border-radius: 10px !important;
            margin-bottom: 15px !important;
        }

        /* フッター */
        .custom-footer {
            margin-top: 30px; color: #888888; text-align: center;
            font-size: 10px; padding-bottom: 40px;
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

    # --- ヘッダーエリアの描画 ---
    # ここで直接描画することで、謎の空カードが発生するのを防ぎます
    st.markdown("""
        <div class="custom-header-card">
            <div class="header-flex">
                <div class="logo-box"><span class="logo-h">H</span><span class="logo-imai">IMAI</span></div>
                <div>
                    <div class="header-title">今井社会保険労務士事務所</div>
                    <div class="header-subtitle">就業規則・労務リスク判定 AIアシスタント</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # サイドバーにログアウト
    with st.sidebar:
        logout()

    # --- Dify 連携ロジック ---
    try:
        D_KEY = st.secrets["DIFY_API_KEY"]
    except:
        st.error("DIFY_API_KEYが設定されていません。")
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

    # チャット入力
    if prompt := st.chat_input("就業規則の条文を入力してください..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                response = requests.post(
                    "https://api.dify.ai/v1/chat-messages",
                    headers={"Authorization": f"Bearer {D_KEY}", "Content-Type": "application/json"},
                    json={"inputs": {}, "query": prompt, "response_mode": "blocking", "user": st.session_state.user_id},
                    timeout=60
                )
                response.raise_for_status()
                answer = response.json().get("answer", "回答を取得できませんでした。")
                
                st.markdown(answer)
                display_disclaimer() # ★ここで確実に出るようにしています
                
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

    # フッター
    st.markdown('<div class="custom-footer">© 2024 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office</div>', unsafe_allow_html=True)