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
        </style>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.markdown(
        """
        <div class="app-title">
            <span class="icon">📊</span>
            <h1>分析くん</h1>
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
        pg = st.navigation([
                        st.Page("app_pages/agents.py",
                                title="Agents", icon="⚙️"),
                        st.Page("app_pages/chat.py",
                                title="Chat",
                                icon="🤖")])
        pg.run()


# アプリを起動
main()
