import streamlit as st
from state import init_state

def main():
    st.set_page_config(
        page_title="CA API App",
        page_icon="🗣️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # サイドバーにアプリ名を表示
    st.sidebar.markdown(
        """
        <div style="text-align: center; padding: 1rem 0 1.5rem 0;">
            <span style="font-size: 2.5rem;">📊</span>
            <h1 style="margin: 0.3rem 0 0 0; font-size: 1.8rem; font-weight: 700;">分析さん</h1>
            <p style="margin: 0; font-size: 0.8rem; color: #888;">Data Analytics Assistant</p>
        </div>
        <hr style="margin: 0 0 1rem 0; border: none; border-top: 1px solid #333;">
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
