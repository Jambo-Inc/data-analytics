"""
グローバル状態管理モジュール
st.session_stateを使用してAPIクライアント、エージェント、会話、メッセージを管理する
"""
import streamlit as st
from google.cloud import geminidataanalytics
from google.api_core import exceptions as google_exceptions

def init_state():
    """
    セッション状態を初期化する（セッション開始時に1回だけ実行）

    処理内容:
    1. APIクライアント（DataAgentServiceClient, DataChatServiceClient）を作成
    2. 既存のエージェント一覧を取得
    3. 最新のエージェントを選択し、その会話一覧を取得
    4. 最新の会話を選択し、そのメッセージ一覧を取得
    """
    state = st.session_state

    state.agents = []
    state.convos = []
    state.convo_messages = []

    state.agent_client = geminidataanalytics.DataAgentServiceClient()
    state.chat_client = geminidataanalytics.DataChatServiceClient()

    fetch_agents_state(rerun=False)

    state.current_agent = None
    if state.agents:
        state.current_agent = state.agents[-1]

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
