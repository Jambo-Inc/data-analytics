"""
グローバル状態管理モジュール
st.session_stateを使用してAPIクライアント、エージェント、会話、メッセージを管理する
"""
import uuid
import streamlit as st
from google.cloud import geminidataanalytics
from google.cloud import bigquery
from google.api_core import exceptions as google_exceptions
from utils.templates import load_template

# 固定エージェント用のテンプレートファイル名
DEFAULT_TEMPLATE = "jambo_default.yaml"
# 固定エージェントの表示名
DEFAULT_AGENT_NAME = "JamboGPT"

def init_state():
    """
    セッション状態を初期化する（セッション開始時に1回だけ実行）

    処理内容:
    1. APIクライアント（DataAgentServiceClient, DataChatServiceClient）を作成
    2. 既存のエージェントを取得、なければテンプレートから自動作成
    3. 固定エージェントの会話一覧を取得
    4. 最新の会話を選択し、そのメッセージ一覧を取得
    """
    state = st.session_state

    state.agents = []
    state.convos = []
    state.convo_messages = []

    state.agent_client = geminidataanalytics.DataAgentServiceClient()
    state.chat_client = geminidataanalytics.DataChatServiceClient()

    fetch_agents_state(rerun=False)

    # エージェントがなければテンプレートから自動作成
    if not state.agents:
        _create_default_agent()
        fetch_agents_state(rerun=False)

    # 固定エージェントを設定
    state.current_agent = state.agents[0] if state.agents else None

    if state.current_agent:
        fetch_convos_state(agent=state.current_agent, rerun=False)

    state.current_convo = None
    if state.convos:
        state.current_convo = state.convos[0]

    if state.current_convo:
        fetch_messages_state(convo=state.current_convo, rerun=False)

    # 初期化完了フラグを設定し、画面を再描画
    state.initialized = True
    st.rerun()


def _create_default_agent():
    """
    デフォルトテンプレートからエージェントを自動作成する
    """
    state = st.session_state
    template = load_template(DEFAULT_TEMPLATE)
    if not template:
        st.error(f"テンプレート {DEFAULT_TEMPLATE} が見つかりません")
        return

    project_id = st.secrets.cloud.project_id

    # エージェントオブジェクトを作成
    agent = geminidataanalytics.DataAgent()
    agent_id = f"a{uuid.uuid4()}"
    agent.name = f"projects/{project_id}/locations/global/dataAgents/{agent_id}"
    agent.display_name = DEFAULT_AGENT_NAME
    agent.description = template.description

    # コンテキスト（データソースとシステム指示）を設定
    published_context = geminidataanalytics.Context()
    datasource_references = geminidataanalytics.DatasourceReferences()

    # BigQueryテーブルへの参照を作成
    table_references = []
    for t in template.tables:
        bigquery_table_reference = geminidataanalytics.BigQueryTableReference()
        bigquery_table_reference.project_id = t.project_id
        bigquery_table_reference.dataset_id = t.dataset_id
        bigquery_table_reference.table_id = t.table_id
        table_references.append(bigquery_table_reference)

    datasource_references.bq.table_references = table_references
    published_context.datasource_references = datasource_references
    published_context.system_instruction = template.system_preamble

    agent.data_analytics_agent.published_context = published_context

    # APIにエージェント作成リクエストを送信
    request = geminidataanalytics.CreateDataAgentRequest(
        parent=f"projects/{project_id}/locations/global",
        data_agent_id=agent_id,
        data_agent=agent
    )

    try:
        state.agent_client.create_data_agent(request=request)
    except google_exceptions.GoogleAPICallError as e:
        st.error(f"エージェント自動作成エラー: {e}")
    except Exception as e:
        st.error(f"予期しないエラー: {e}")


def fetch_agents_state(rerun=True):
    """
    全てのデータエージェントを取得してセッション状態に保存する

    引数:
        rerun: Trueの場合、取得後に画面を再描画する
    """
    state = st.session_state
    client = state.agent_client
    project_id = st.secrets.cloud.project_id

    try:
        request = geminidataanalytics.ListDataAgentsRequest(
            parent=f"projects/{project_id}/locations/global"
        )
        agents = list(client.list_data_agents(request=request))
        state.agents = agents if len(agents) > 0 else []
        if rerun:
            st.rerun()
    except google_exceptions.GoogleAPICallError as e:
        st.error(f"API error fetching agents: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")


def fetch_convos_state(agent=None, rerun=True):
    """
    指定されたエージェントの会話一覧を取得する（最大100件）

    引数:
        agent: 対象のエージェント（Noneの場合は何もしない）
        rerun: Trueの場合、取得後に画面を再描画する
    """
    if agent is None:
        return

    state = st.session_state
    state.convos = []
    client = state.chat_client
    project_id = st.secrets.cloud.project_id

    try:
        # 会話一覧を取得（TODO: フィルタ機能が動作したら修正）
        request = geminidataanalytics.ListConversationsRequest(
            parent=f"projects/{project_id}/locations/global",
            page_size=100,
        )

        convos = list(client.list_conversations(request=request))
        # 指定されたエージェントに属する会話のみをフィルタリング
        convos = [c for c in convos if c.agents[0] == agent.name]
        state.convos = convos if len(convos) > 0 else []
        if rerun:
            st.rerun()

    except google_exceptions.GoogleAPICallError as e:
        st.error(f"API error fetching convos: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")


def fetch_messages_state(convo=None, rerun=True):
    """
    指定された会話のメッセージ一覧を取得する

    引数:
        convo: 対象の会話（Noneの場合は何もしない）
        rerun: Trueの場合、取得後に画面を再描画する
    """
    if convo is None:
        return

    state = st.session_state
    state.convo_messages = []
    client = state.chat_client
    request = geminidataanalytics.ListMessagesRequest(parent=convo.name)

    try:
        msgs = list(client.list_messages(request=request))
        # メッセージオブジェクトから実際のメッセージ内容を取得
        msgs = [m.message for m in msgs]
        # 時系列順に並び替え（APIは新しい順で返すため逆順にする）
        state.convo_messages = list(reversed(msgs)) if len(msgs) > 0 else []
        if rerun:
            st.rerun()
    except google_exceptions.GoogleAPICallError as e:
        st.error(f"API error fetching messages: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")


def create_convo(agent=None):
    """
    新しい会話を作成し、会話一覧の先頭に追加する

    引数:
        agent: 会話を紐付けるエージェント

    戻り値:
        作成された会話オブジェクト（エラー時はNone）
    """
    state = st.session_state
    client = state.chat_client
    project_id = st.secrets.cloud.project_id

    # 会話オブジェクトを作成し、エージェントを紐付け
    conversation = geminidataanalytics.Conversation()
    conversation.agents = [agent.name]

    request = geminidataanalytics.CreateConversationRequest(
        parent=f"projects/{project_id}/locations/global",
        conversation=conversation,
    )

    try:
        # 会話を作成し、一覧の先頭に追加
        convo = client.create_conversation(request=request)
        state.convos.insert(0, convo)
        return convo
    except google_exceptions.GoogleAPICallError as e:
        st.error(f"API error creating convo: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")


@st.cache_data(ttl=3600)
def fetch_reference_data():
    """
    referenceデータセットのマスタテーブルを取得する（1時間キャッシュ）

    戻り値:
        dict: {
            "application_name": DataFrame（アプリID→名前のマッピング）,
            "log_point_type": DataFrame（アクション種別のマスタ）
        }
    """
    project_id = st.secrets.cloud.project_id
    client = bigquery.Client(project=project_id)

    result = {}

    # application_nameテーブルを取得
    try:
        query_app = f"""
            SELECT application_id, application_name
            FROM `{project_id}.reference.application_name`
            ORDER BY CAST(application_id AS INT64)
        """
        result["application_name"] = client.query(query_app).to_dataframe(create_bqstorage_client=False)
    except Exception as e:
        st.error(f"application_name取得エラー: {e}")
        result["application_name"] = None

    # log_point_typeテーブルを取得
    try:
        query_type = f"""
            SELECT type, action_name
            FROM `{project_id}.reference.log_point_type`
            ORDER BY CAST(type AS INT64)
        """
        result["log_point_type"] = client.query(query_type).to_dataframe(create_bqstorage_client=False)
    except Exception as e:
        st.error(f"log_point_type取得エラー: {e}")
        result["log_point_type"] = None

    return result
