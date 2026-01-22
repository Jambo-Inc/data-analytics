import streamlit as st
from state import init_state

def main():
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
            <h1>分析さん</h1>
            <p>Data Analytics Assistant</p>
            <hr>
        </div>
        """,
        unsafe_allow_html=True
    )

    if "initialized" not in st.session_state:
        with st.spinner("Loading"):
            init_state()
    else:
        pg = st.navigation([
                        st.Page("app_pages/agents.py",
                                title="Agents", icon="⚙️"),
                        st.Page("app_pages/chat.py",
                                title="Chat",
                                icon="🤖")])
        pg.run()

main()
