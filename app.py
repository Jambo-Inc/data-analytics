"""
アプリのメインエントリーポイント
Streamlitアプリの初期設定とページナビゲーションを管理する
"""
import streamlit as st
from state import init_state


def main():
    """
    アプリのメイン関数
    - ページ設定（タイトル、アイコン、レイアウト）を行う
    - サイドバーにアプリ名「分析くん」を表示する
    - 初回起動時は状態を初期化し、以降はページナビゲーションを表示する
    """
    st.set_page_config(
        page_title="CA API App",
        page_icon="🗣️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # サイドバーにアプリ名を表示（ナビゲーションより上に配置）
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                padding-top: 0 !important;
            }
            .app-title {
                text-align: center;
                padding: 1rem 1rem 1.5rem 1rem;
            }
            .app-title .icon { font-size: 2.5rem; }
            .app-title h1 { margin: 0.3rem 0 0 0; font-size: 1.8rem; font-weight: 700; }
            .app-title p { margin: 0; font-size: 0.8rem; color: #888; }
            .app-title hr { margin: 1rem 0 0 0; border: none; border-top: 1px solid #333; }
            /* 新規チャットボタンのスタイル */
            .new-chat-container {
                position: relative;
                margin-top: -0.5rem;
                margin-bottom: 1rem;
            }
            .new-chat-btn {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                border: 1px solid #555;
                border-radius: 0.5rem;
                background: transparent;
                color: inherit;
                cursor: pointer;
                font-size: 0.9rem;
                transition: background 0.2s, border-color 0.2s;
                width: 100%;
                justify-content: center;
            }
            .new-chat-btn:hover {
                background: rgba(255,255,255,0.1);
                border-color: #888;
            }
            .new-chat-btn svg {
                width: 16px;
                height: 16px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.markdown(
        """
        <div class="app-title">
            <span class="icon">📊</span>
            <h1>分析くん(仮)</h1>
            <p>Data Analytics Assistant</p>
            <hr>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 初回起動時：状態を初期化（APIクライアントの作成、既存エージェント・会話の取得）
    if "initialized" not in st.session_state:
        with st.spinner("Loading"):
            init_state()
    else:
        # 初期化済み：ページナビゲーションを表示
        # - Agents: データエージェントの作成・編集・削除
        # - Chat: エージェントとのチャット
        agents_page = st.Page("app_pages/agents.py", title="Agents", icon="⚙️")
        chat_page = st.Page("app_pages/chat.py", title="Chat", icon="🤖", default=True)
        pg = st.navigation([agents_page, chat_page])

        # サイドバーに新規チャットボタンを追加
        with st.sidebar:
            if st.button(
                "✏️ 新規チャット",
                key="new_chat_sidebar_btn",
                use_container_width=True,
                disabled=len(st.session_state.get("agents", [])) == 0
            ):
                # 新規チャットフラグを設定してChatページに遷移
                st.session_state.start_new_chat = True
                st.switch_page(chat_page)

        pg.run()


# アプリを起動
main()
