"""
チャットページ
エージェントとの対話UI、会話の選択・作成、メッセージの表示を行う
"""
import streamlit as st
from google.cloud import geminidataanalytics
from state import create_convo, fetch_convos_state, fetch_messages_state
from utils.chat import show_message

# セッション状態のキー定義
AGENT_SELECT_KEY = "agent_selectbox_value"  # エージェント選択用
CONVO_SELECT_KEY = "agent_convo_value"      # 会話選択用


def handle_agent_select():
    """
    エージェント選択時のコールバック
    選択されたエージェントを設定し、そのエージェントの会話一覧を取得する
    """
    state = st.session_state
    state.current_agent = state[AGENT_SELECT_KEY]
    state.current_convo = None
    state.convo_messages = []
    st.spinner("Fetching past conversations")
    fetch_convos_state(state.current_agent, False)
    # 会話がある場合は最新の会話を選択し、メッセージを取得
    if len(state.convos) > 0:
        st.spinner("Fetching last conversation's messages")
        state.current_convo = state.convos[0]
        fetch_messages_state(state.current_convo, False)


def handle_convo_select():
    """
    会話選択時のコールバック
    選択された会話を設定し、そのメッセージ一覧を取得する
    """
    state = st.session_state
    state.current_convo = state[CONVO_SELECT_KEY]
    state.convo_messages = []
    st.spinner("Fetching past message")
    fetch_messages_state(state.current_convo, False)


def handle_create_convo():
    """
    新規会話作成ボタンのコールバック
    現在のエージェントに紐づく新しい会話を作成する
    """
    state = st.session_state
    st.spinner("Creating new convo")
    state.current_convo = create_convo(agent=state.current_agent)
    state.convo_messages = []


def conversations_main():
    """
    チャット画面のメイン関数

    機能:
    1. エージェント・会話の選択ドロップダウン
    2. チャット履歴の表示
    3. ユーザー入力の受付とAIレスポンスの表示
    """
    state = st.session_state

    # エージェントが存在しない場合は警告を表示して終了
    if len(state.agents) == 0:
        st.warning("Please create an agent first before chatting")
        st.stop()

    # ========================================
    # エージェント・会話選択バー
    # ========================================
    with st.container(
        border=True,
        horizontal=True,
        horizontal_alignment="distribute"
    ):
        def get_agent_display_name(a):
            """エージェントの表示名を取得（なければリソース名からIDを抽出）"""
            return getattr(a, 'display_name', None) or a.name.split('/')[-1]

        # エージェントを表示名でソート
        sorted_agents = sorted(state.agents, key=get_agent_display_name)

        # 現在選択中のエージェントのインデックスを取得
        agent_index = None
        if state.current_agent:
            for index, agent in enumerate(sorted_agents):
                if state.current_agent.name == agent.name:
                    agent_index = index
            # エージェントが見つからない場合は選択をクリア
            if agent_index is None:
                state.current_agent = None
                state.current_convo = None
                state.convo_messages = []

        # エージェント選択ドロップダウン
        st.selectbox(
            "Select agent to chat with:",
            sorted_agents,
            index=agent_index,
            key=AGENT_SELECT_KEY,
            format_func=get_agent_display_name,
            on_change=handle_agent_select
        )

        # 現在選択中の会話のインデックスを取得
        convo_index = None
        if state.current_convo:
            for index, convo in enumerate(state.convos):
                if state.current_convo.name == convo.name:
                    convo_index = index

        # 会話選択ドロップダウン（最終使用日時でソート済み）
        st.selectbox(
            "Select previous conversation with agent (by last used):",
            state.convos,
            index=convo_index,
            key=CONVO_SELECT_KEY,
            format_func=lambda c: c.last_used_time.strftime("%m/%d/%Y, %H:%M:%S"),
            on_change=handle_convo_select
        )
        # 新規会話作成ボタン
        st.button(
            "新しいチャット",
            on_click=handle_create_convo,
            disabled=len(state.agents) == 0
        )

    # ========================================
    # チャット表示エリア
    # ========================================
    # サブヘッダーに会話の開始日時を表示
    subheader_string = "Chat"
    if state.current_convo:
        subheader_string = f'Chat - Conversation started at {state.current_convo.create_time.strftime("%m/%d/%Y, %H:%M:%S")}'

    st.subheader(subheader_string)

    # エージェントが選択されていない場合は警告を表示
    if state.current_agent is None:
        st.warning("Please select an agent above to chat with")
        st.stop()

    # チャット履歴を表示（ユーザーメッセージとアシスタントメッセージを区別）
    for message in state.convo_messages:
        if "system_message" in message:
            with st.chat_message("assistant"):
                show_message(message)
        else:
            with st.chat_message("user"):
                st.markdown(message.user_message.text)

    # ========================================
    # チャット入力エリア
    # ========================================
    user_input = st.chat_input("What would you like to know?")

    if user_input:
        # 会話がない場合は新規作成
        if len(state.convos) == 0:
            handle_create_convo()

        # ユーザーメッセージを履歴に追加して表示
        state.convo_messages.append(geminidataanalytics.Message(user_message={"text": user_input}))
        with st.chat_message("user"):
            st.markdown(user_input)

        # アシスタントのレスポンスを生成・表示
        with st.chat_message("assistant"):
            with st.spinner("Thinking... 🤖"):
                # チャットリクエストを作成
                user_msg = geminidataanalytics.Message(user_message={"text": user_input})
                convo_ref = geminidataanalytics.ConversationReference()
                convo_ref.conversation = state.current_convo.name
                convo_ref.data_agent_context.data_agent = state.current_agent.name

                # Lookerエージェントの場合はOAuth認証情報を追加
                if is_looker_agent(state.current_agent):
                    credentials = geminidataanalytics.Credentials()
                    credentials.oauth.secret.client_id = st.secrets.looker.client_id
                    credentials.oauth.secret.client_secret = st.secrets.looker.client_secret
                    convo_ref.data_agent_context.credentials = credentials

                # APIにリクエストを送信し、ストリーミングでレスポンスを取得
                req = geminidataanalytics.ChatRequest(
                    parent=f"projects/{st.secrets.cloud.project_id}/locations/global",
                    messages=[user_msg],
                    conversation_reference=convo_ref,
                )
                # レスポンスを順次表示し、履歴に追加
                for message in state.chat_client.chat(request=req):
                    show_message(message)
                    state.convo_messages.append(message)
            # 画面を再描画して履歴を更新
            st.rerun()


def is_looker_agent(agent) -> bool:
    """
    エージェントがLookerデータソースを使用しているか判定する

    引数:
        agent: 判定対象のエージェント

    戻り値:
        LookerデータソースならTrue、それ以外はFalse
    """
    datasource_references = agent.data_analytics_agent.published_context.datasource_references

    return "looker" in datasource_references


# ページを実行
conversations_main()
