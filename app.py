import streamlit as st
import requests
import uuid
import base64
from auth import check_password, logout

# --- 1. ページ設定 ---
st.set_page_config(page_title="労務リスク判定 AI", page_icon="⚖️", layout="centered")

# --- 2. 認証チェック ---
if check_password():
    
    # --- デザインCSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #ffffff; }
        
        /* ヘッダー：白ベースでロゴと文字を横並び */
        .header-container {
            display: flex;
            align-items: center;
            justify-content: flex-start;
            padding: 60px 0px 20px 0px;
            border-bottom: 2px solid #f0f2f6;
            margin-bottom: 30px;
        }
        
        /* ロゴ画像用のスタイル */
        .logo-img {
            height: 60px;
            margin-right: 20px;
        }

        .title-text-box {
            display: flex;
            flex-direction: column;
        }

        .header-title {
            color: #061e3d;
            font-size: 24px;
            font-weight: 700;
            margin: 0;
            line-height: 1.2;
        }

        .header-subtitle {
            color: #666666;
            font-size: 14px;
            margin-top: 4px;
        }
        
        /* 免責事項ボックス：確実に見えるように枠線を強調 */
        .disclaimer-box {
            background-color: #f8f9fa;
            border-left: 5px solid #061e3d;
            padding: 15px;
            margin: 15px 0 30px 0;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .disclaimer-text {
            color: #444444;
            font-size: 11px;
            line-height: 1.7;
            margin: 0;
        }

        .footer {
            position: fixed; bottom: 0; left: 0; width: 100%;
            background-color: #061e3d; color: white; text-align: center;
            padding: 10px 0; font-size: 11px; z-index: 100;
        }
        
        .block-container { padding-top: 0rem !important; padding-bottom: 6rem !important; }
        
        /* チャット吹き出しの調整 */
        .stChatMessage { margin-bottom: -10px !important; }
        </style>
        """, unsafe_allow_html=True)

    # ロゴとタイトルの表示
    # ※IMAIロゴ3.jpgのイメージをCSSとテキストで再現（画像リンク切れを防ぐため）
    st.markdown(f"""
        <div class="header-container">
            <div style="display: flex; align-items: center;">
                <div style="background-color:#061e3d; color:white; padding:10px; border-radius:5px; margin-right:15px; font-family:serif; font-weight:900; font-size:30px; line-height:1; text-align:center;">
                    H<br><span style="font-size:10px;">IMAI</span>
                </div>
                <div class="title-text-box">
                    <div class="header-title">今井社会保険労務士事務所</div>
                    <div class="header-subtitle">就業規則・労務リスク判定 AIアシスタント</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    logout()

    # --- 免責事項表示用関数（最新版） ---
    def display_disclaimer():
        st.markdown("""
            <div class="disclaimer-box">
                <p class="disclaimer-text">
                    <strong>【AI判定に関する重要事項】</strong><br>
                    本システムは、当事務所が監修した<strong>最新の就業規則ナレッジ（RAG）を直接参照</strong>しており、一般的なAIに比べ高い正確性を備えています。<br>
                    しかしながら、本回答はAIによる推論であり法的助言を確定させるものではありません。個別の事案（具体的な背景や運用状況）に対する最終的な判断については、必ず当事務所の社会保険労務士にご確認ください。<br>
                    本システムの使用により生じた損害について、当事務所は一切の責任を負いかねます。
                </p>
            </div>
        """, unsafe_allow_html=True)

    # --- Dify API 設定 ---
    try:
        D_KEY = st.secrets["DIFY_API_KEY"]
    except:
        st.error("APIキーが設定されていません。")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())

    # --- 履歴表示 ---
    # ループの中で、AIの回答の直後に必ず免責事項を差し込む
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
        if msg["role"] == "assistant":
            display_disclaimer()

    # --- チャット入力 ---
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
                response.raise_for_status()
                answer = response.json().get("answer", "回答を取得できませんでした。")
                
                res_box.markdown(answer)
                display_disclaimer()
                
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"接続エラー: {e}")
                
    st.markdown('<div class="footer">© 2024 IMAI HISAICHIRO Certified Social Insurance and Labor Consultant Office</div>', unsafe_allow_html=True)