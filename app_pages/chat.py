"""
チャットページ
エージェントとの対話UI、会話の選択・作成、メッセージの表示を行う
"""
import streamlit as st
from google.cloud import geminidataanalytics
from state import create_convo, fetch_messages_state
from utils.chat import show_message

# セッション状態のキー定義
CONVO_SELECT_KEY = "agent_convo_value"      # 会話選択用


def show_welcome_message():
    """
    新規チャット時にウェルカムメッセージと質問例を表示する
    """
    st.markdown("""
### 👋 こんにちは！JamboGPTです

私はJamboのポイントログを対象に、データ探索をサポートします。\n
SQLを書かなくても、自然言語で直感的にデータを調べることができます。\n
気になることは、そのまま日本語で聞いてみてください！

---

接続しているデータはこんな感じです：
- 📊 **ポイントログ** - ユーザー×相手×アクション×日ごとの集計データ
  - ユーザー情報: user_id, user_gender, user_name, user_app など
  - 相手情報: partner_id, partner_gender, partner_name, partner_app など
  - アクション: action_name（ビデオ通話、メッセージ送信など）, total_point, interaction_count

---

#### 💡 質問の例

> 「昨日最もポイントを消費した男性ユーザー上位3名を教えて」

> 「user_id=12345678は昨日どういう相手と頻繁にやりとりした？」

> 「昨日Connectで最もビデオ通話を行ったユーザーを上位20名教えて」

---

#### 🎯 うまく回答を得るコツ

- **範囲を絞る** → 「昨日」「今週」「上位10件」など期間や件数を指定すると高速に
- **シンプルに聞く** → 一度に複数の質問をせず、1つずつ聞くのがおすすめ
- **user_idを指定する** → 特定ユーザーを調べたいときは `user_id=12345678` のように指定すると調べやすい
- **毎回完結した質問をする** → 前回の質問内容はあまり覚えていないので、毎回必要な情報を含めて質問すると確実

---

#### 🔄 結果がうまく返ってこなかったら

- **質問を変えてみる** → より直接的に、集計したい内容をシンプルに伝えてみてください。左サイドバーの「参照データ」でアプリIDやアクション種別の対応表を確認できます
- **それでもダメなら** → このアプリを作った人に教えてください！改善の参考にします

何でも聞いてくださいね！
""")


def build_guardrail_message(original_message: str, agent) -> str:
    """
    ユーザーメッセージにガードレール（システム指示）を付加する

    引数:
        original_message: ユーザーが入力した元のメッセージ
        agent: 現在選択中のエージェント

    戻り値:
        ガードレール付きのメッセージ（システム指示がない場合は元のメッセージ）
    """
    system_instruction = ""
    try:
        system_instruction = agent.data_analytics_agent.published_context.system_instruction or ""
    except AttributeError:
        pass

    if not system_instruction:
        return original_message

    return f"""【以下のルールを必ず遵守してください】
{system_instruction}

【ユーザーの質問】
{original_message}"""


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
    1. チャット履歴の表示
    2. ユーザー入力の受付とAIレスポンスの表示
    """
    state = st.session_state

    # エージェントが存在しない場合は警告を表示して終了
    if not state.current_agent:
        st.warning("エージェントの初期化中にエラーが発生しました")
        st.stop()

    # サイドバーの新規チャットボタンからの遷移を処理
    if state.get("start_new_chat"):
        state.start_new_chat = False  # フラグをリセット
        handle_create_convo()

    # ========================================
    # チャット表示エリア
    # ========================================
    # 新規チャット時はウェルカムメッセージを表示
    if not state.convo_messages:
        show_welcome_message()

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
        if not state.current_convo:
            handle_create_convo()

        # ユーザーメッセージを履歴に追加して表示
        state.convo_messages.append(geminidataanalytics.Message(user_message={"text": user_input}))
        with st.chat_message("user"):
            st.markdown(user_input)

        # アシスタントのレスポンスを生成・表示
        with st.chat_message("assistant"):
            with st.spinner("Thinking... 🤖"):
                # チャットリクエストを作成（ガードレール付きメッセージを使用）
                augmented_message = build_guardrail_message(user_input, state.current_agent)
                user_msg = geminidataanalytics.Message(user_message={"text": augmented_message})
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


