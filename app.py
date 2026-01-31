"""
アプリのメインエントリーポイント
Streamlitアプリの初期設定とページナビゲーションを管理する
"""
import os
import streamlit as st
from google.cloud import geminidataanalytics
from state import init_state, fetch_messages_state, fetch_agents_state, create_convo
from utils.templates import list_templates, load_template


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

    # サイドバーのスタイル
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                display: none !important;
            }
            .app-title {
                text-align: center;
                padding: 1rem 1rem 1.5rem 1rem;
            }
            .app-title .icon { font-size: 2.5rem; }
            .app-title h1 { margin: 0.3rem 0 0 0; font-size: 1.8rem; font-weight: 700; }
            .app-title p { margin: 0; font-size: 0.8rem; color: #888; }
            .app-title hr { margin: 1rem 0 0 0; border: none; border-top: 1px solid #333; }
            /* 会話履歴のスタイル */
            .chat-history-label {
                font-size: 0.75rem;
                color: #888;
                margin: 1rem 0 0.5rem 0;
                text-transform: uppercase;
                letter-spacing: 0.05em;
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

    # 初回起動時：状態を初期化（APIクライアントの作成、エージェントの自動作成・取得）
    if "initialized" not in st.session_state:
        with st.spinner("Loading"):
            init_state()
    else:
        # サイドバーに新規チャットボタンと会話履歴を追加
        with st.sidebar:
            # エージェント更新ボタン（テンプレートで再作成＋新規チャット）- ローカル開発時のみ表示
            templates = list_templates()
            if templates and os.environ.get("DEBUG"):
                if st.button("🔄 エージェントを更新", key="rebuild_agent_btn", use_container_width=True):
                    template = load_template(templates[0])  # 最初のテンプレートを使用
                    if template:
                        try:
                            # 古いエージェントを削除
                            for ag in st.session_state.get("agents", []):
                                delete_req = geminidataanalytics.DeleteDataAgentRequest(name=ag.name)
                                st.session_state.agent_client.delete_data_agent(request=delete_req).result()

                            # 新しいエージェントを作成
                            import uuid
                            agent = geminidataanalytics.DataAgent()
                            agent_id = f"a{uuid.uuid4()}"
                            agent.name = f"projects/{st.secrets.cloud.project_id}/locations/global/dataAgents/{agent_id}"
                            agent.display_name = template.name
                            agent.description = template.description

                            published_context = geminidataanalytics.Context()
                            datasource_references = geminidataanalytics.DatasourceReferences()
                            table_references = []
                            for t in template.tables:
                                ref = geminidataanalytics.BigQueryTableReference()
                                ref.project_id = t.project_id
                                ref.dataset_id = t.dataset_id
                                ref.table_id = t.table_id
                                table_references.append(ref)
                            datasource_references.bq.table_references = table_references
                            published_context.datasource_references = datasource_references
                            published_context.system_instruction = template.system_preamble
                            agent.data_analytics_agent.published_context = published_context

                            create_req = geminidataanalytics.CreateDataAgentRequest(
                                parent=f"projects/{st.secrets.cloud.project_id}/locations/global",
                                data_agent_id=agent_id,
                                data_agent=agent
                            )
                            st.session_state.agent_client.create_data_agent(request=create_req).result()

                            # 状態をリセットして新規チャット開始
                            fetch_agents_state(rerun=False)
                            st.session_state.current_agent = st.session_state.agents[0] if st.session_state.agents else None
                            st.session_state.convos = []
                            st.session_state.convo_messages = []
                            # 新しい会話を作成
                            st.session_state.current_convo = create_convo(agent=st.session_state.current_agent)
                            st.success("エージェントを更新しました")
                            st.rerun()
                        except Exception as e:
                            st.error(f"エラー: {e}")

                st.divider()

            # 新規チャットボタン
            if st.button(
                "✏️ 新規チャット",
                key="new_chat_sidebar_btn",
                use_container_width=True,
            ):
                st.session_state.start_new_chat = True
                st.rerun()

            # 会話履歴
            convos = st.session_state.get("convos", [])
            if convos:
                st.markdown('<p class="chat-history-label">会話履歴</p>', unsafe_allow_html=True)
                for convo in convos:
                    # 会話の表示名（作成日時）
                    convo_label = convo.create_time.strftime("%m/%d %H:%M")
                    # 現在選択中の会話かどうか
                    is_current = (
                        st.session_state.current_convo and
                        st.session_state.current_convo.name == convo.name
                    )
                    # ボタンのスタイル（選択中は強調）
                    button_type = "primary" if is_current else "secondary"
                    if st.button(
                        f"💬 {convo_label}",
                        key=f"convo_{convo.name}",
                        use_container_width=True,
                        type=button_type,
                    ):
                        # 会話を切り替え
                        st.session_state.current_convo = convo
                        st.session_state.convo_messages = []
                        fetch_messages_state(convo, rerun=False)
                        st.rerun()

        # チャットページを直接実行（ナビゲーションなし）
        import app_pages.chat as chat_module
        chat_module.conversations_main()


# アプリを起動
main()
