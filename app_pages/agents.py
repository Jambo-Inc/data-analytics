"""
データエージェント管理ページ
エージェントの一覧表示、作成、更新、削除を行う
"""
import streamlit as st
from google.api_core import exceptions as google_exceptions
from google.cloud import geminidataanalytics
from state import fetch_agents_state
from utils.agents import get_time_delta_string
import uuid

# データソースの種類を定義
BIG_QUERY = "BigQuery"
LOOKER = "Looker"


def agents_main():
    """
    エージェント管理画面のメイン関数

    機能:
    1. 既存エージェントの一覧表示と編集・削除
    2. 新規エージェントの作成フォーム
    """
    state = st.session_state

    # ヘッダー部分：タイトルと更新ボタン
    with st.container(horizontal=True, horizontal_alignment="distribute"):
        st.subheader("Data agents available")
        if st.button("Refresh agents"):
            with st.spinner("Refreshing..."):
                fetch_agents_state()

    # エージェント一覧を表示するコンテナ
    with st.container(border=True, height=450):
        if len(state.agents) == 0:
            st.write("There are no agents available.")
        # 各エージェントを展開可能なパネルとして表示
        for ag in state.agents:
            # 表示名がなければリソースIDから名前部分を取得
            name = ag.display_name or ag.name.split("/")[-1]
            with st.expander(f"**{name}**"):
                col1, col2 = st.columns([1, 2])
                # 左カラム：基本情報（ID、表示名、説明、作成/更新日時）
                with col1:
                    st.write(f"**Resource ID:** {ag.name}")
                    display_name = st.text_input(
                        "**Display name:**",
                        value=ag.display_name,
                        key=f"updatedisp-{ag.name}"
                    )
                    description = st.text_input(
                        "**Description:**",
                        value=ag.description,
                        key=f"updatedesc-{ag.name}"
                    )
                    st.write(f"**Created:** {get_time_delta_string(ag.create_time, 'Just created')}")
                    st.write(f"**Updated:** {get_time_delta_string(ag.update_time, 'Just updated')}")
                # 右カラム：システム指示とデータソース
                with col2:
                    system_instruction = st.text_area(
                        "**System instructions:** *(drag the bottom right corner to enlarge text input)*",
                        value=ag.data_analytics_agent.published_context.system_instruction,
                        key=f"updatesys-{ag.name}"
                    )
                    st.text_area(
                        "**Data source:**",
                        value=ag.data_analytics_agent.published_context.datasource_references,
                        disabled=True,
                        key=f"datasrc-{ag.name}"
                    )
                    # 更新・削除ボタンを横並びで配置
                    with st.container(horizontal=True, horizontal_alignment="distribute"):
                        # エージェント更新ボタン
                        if st.button("**Update agent**", key=f"update-{ag.name}"):
                            # 更新用のエージェントオブジェクトを作成
                            agent = geminidataanalytics.DataAgent()
                            agent.name = ag.name
                            agent.display_name = display_name
                            agent.description = description

                            # コンテキスト（システム指示とデータソース）を設定
                            published_context = geminidataanalytics.Context()
                            published_context.datasource_references = ag.data_analytics_agent.published_context.datasource_references
                            published_context.system_instruction = system_instruction
                            agent.data_analytics_agent.published_context = published_context

                            # APIに更新リクエストを送信
                            request = geminidataanalytics.UpdateDataAgentRequest(data_agent=agent, update_mask="*")

                            try:
                                state.agent_client.update_data_agent(request=request).result()
                                fetch_agents_state()
                                st.success("Succesfully updated data agent")
                            except Exception as e:
                                st.error(f"Error updating data agent: {e}")

                        # エージェント削除ボタン（赤色で警告表示）
                        if st.button("**:red[DELETE AGENT]**", key=f"delete-{ag.name}"):
                            request = geminidataanalytics.DeleteDataAgentRequest(
                                name=ag.name
                            )
                            try:
                                operation = state.agent_client.delete_data_agent(request=request).result()
                                fetch_agents_state()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting Data Agent: {e}")

    # ========================================
    # 新規エージェント作成フォーム
    # ========================================
    # 注: st.form()は使用しない（BigQuery/Lookerの動的な入力切り替えに対応できないため）
    st.subheader("Create a data agent")
    with st.container(border=True, key="create_agent_form"):
        col1, col2 = st.columns(2)
        # 左カラム：エージェントの基本情報入力
        with col1:
            display_name = st.text_input("Agent display name:")
            description = st.text_area("Agent description:", height=70)
            system_instruction = st.text_area("Agent system instruction:", height=140)
        # 右カラム：データソース設定
        with col2:
            # データソースの種類を選択（BigQuery or Looker）
            data_source = st.radio(
                "Data source:",
                [BIG_QUERY, LOOKER],
                horizontal=True
            )
            # 選択されたデータソースに応じて入力フィールドを切り替え
            if data_source == BIG_QUERY:
                bq_project_id = st.text_input("BigQuery project ID:", placeholder="bigquery-public-data")
                bq_dataset_id = st.text_input("BigQuery dataset ID:", placeholder="san_francisco_trees")
                bq_table_id = st.text_input("BigQuery table ID:", placeholder="street_trees")
            else:
                looker_instance_url = st.text_input("Looker instance URL:",
                                                     placeholder="myinstance.looker.com")
                looker_model = st.text_input("Looker model:")
                looker_explore = st.text_input("Looker explore:")

        # エージェント作成ボタン
        if st.button("Create agent"):
            # 新規エージェントオブジェクトを作成
            agent = geminidataanalytics.DataAgent()
            # TODO: 数字始まりのIDで会話作成が失敗するバグの修正後、ID/名前の手動設定を削除
            id = f"a{uuid.uuid4()}"
            agent.name = f"projects/{st.secrets.cloud.project_id}/locations/global/dataAgents/{id}"
            agent.display_name = display_name
            agent.description = description

            # コンテキスト（データソースとシステム指示）を設定
            published_context = geminidataanalytics.Context()
            datasource_references = geminidataanalytics.DatasourceReferences()
            # データソースの種類に応じてリファレンスを作成
            if data_source == BIG_QUERY:
                # BigQueryテーブルへの参照を作成
                bigquery_table_reference = geminidataanalytics.BigQueryTableReference()
                bigquery_table_reference.project_id = bq_project_id
                bigquery_table_reference.dataset_id = bq_dataset_id
                bigquery_table_reference.table_id = bq_table_id
                datasource_references.bq.table_references = [bigquery_table_reference]
            else:
                # Looker Exploreへの参照を作成
                looker_explore_reference = geminidataanalytics.LookerExploreReference()
                looker_explore_reference.looker_instance_uri = looker_instance_url
                looker_explore_reference.lookml_model = looker_model
                looker_explore_reference.explore = looker_explore
                datasource_references.looker.explore_references = [looker_explore_reference]

            # コンテキストにデータソースとシステム指示を設定
            published_context.datasource_references = datasource_references
            published_context.system_instruction = system_instruction

            agent.data_analytics_agent.published_context = published_context

            # APIにエージェント作成リクエストを送信
            # TODO: 数字始まりのIDで会話作成が失敗するバグの修正後、ID/名前の手動設定を削除
            request = geminidataanalytics.CreateDataAgentRequest(
                parent=f"projects/{st.secrets.cloud.project_id}/locations/global",
                data_agent_id=id,
                data_agent=agent
            )

            try:
                state.agent_client.create_data_agent(request=request)
                st.success(f"Agent '{display_name}' successfully created")
                fetch_agents_state()
            except google_exceptions.GoogleAPICallError as e:
                st.error(f"API error creating agent: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")


# ページを実行
agents_main()
