"""
チャットレスポンス表示用ユーティリティ
メッセージタイプ（テキスト、スキーマ、データ、チャート）に応じた描画処理を提供する

参考: https://cloud.google.com/gemini/docs/conversational-analytics-api/build-agent-sdk#define_helper_functions
"""
import pandas as pd
import json
import altair as alt

import proto
from google.protobuf.json_format import MessageToDict

import streamlit as st


def handle_text_response(resp):
    """
    テキストレスポンスを表示する
    複数のパーツがある場合は結合してMarkdownで表示
    """
    parts = getattr(resp, 'parts')
    st.markdown(''.join(parts))


def display_schema(data):
    """
    データスキーマ（カラム定義）を展開可能なテーブルとして表示する

    表示内容: カラム名、データ型、説明、モード（NULLABLE等）
    """
    fields = getattr(data, 'fields')
    df = pd.DataFrame({
        "Column": map(lambda field: getattr(field, 'name'), fields),
        "Type": map(lambda field: getattr(field, 'type'), fields),
        "Description": map(lambda field: getattr(field, 'description', '-'), fields),
        "Mode": map(lambda field: getattr(field, 'mode'), fields)
    })
    with st.expander("**Schema**:"):
        st.dataframe(df)


def format_looker_table_ref(table_ref):
    """Lookerデータソースの参照情報を文字列にフォーマットする"""
    return 'lookmlModel: {}, explore: {}, lookerInstanceUri: {}'.format(
        table_ref.lookml_model, table_ref.explore, table_ref.looker_instance_uri)


def format_bq_table_ref(table_ref):
    """BigQueryテーブルの参照情報を「project.dataset.table」形式でフォーマットする"""
    return '{}.{}.{}'.format(table_ref.project_id, table_ref.dataset_id, table_ref.table_id)


def display_datasource(datasource):
    """
    データソース情報を表示する

    対応形式: Studio、Looker Explore、BigQueryテーブル
    データソース名とスキーマを表示
    """
    # データソースの種類を判定してソース名を取得
    source_name = ''
    if 'studio_datasource_id' in datasource:
        source_name = getattr(datasource, 'studio_datasource_id')
    elif 'looker_explore_reference' in datasource:
        source_name = format_looker_table_ref(getattr(datasource, 'looker_explore_reference'))
    else:
        source_name = format_bq_table_ref(getattr(datasource, 'bigquery_table_reference'))

    st.markdown("**Data source**: " + source_name)
    display_schema(datasource.schema)


def handle_schema_response(resp):
    """
    スキーマレスポンスを表示する

    クエリ内容または解決されたスキーマ情報を表示
    """
    if 'query' in resp:
        st.markdown("**Query:** " + resp.query.question)
    elif 'result' in resp:
        st.markdown("**Schema resolved.**")
        for datasource in resp.result.datasources:
            display_datasource(datasource)


def handle_data_response(resp):
    """
    データレスポンスを表示する

    処理内容:
    1. クエリ情報（名前、質問、データソース）を表示
    2. 生成されたSQLを展開可能なコードブロックで表示
    3. 取得したデータをDataFrameテーブルとして表示
    """
    if 'query' in resp:
        # クエリ情報を表示
        query = resp.query
        st.markdown("**Retrieval query**")
        st.markdown('**Query name:** {}'.format(query.name))
        st.markdown('**Question:** {}'.format(query.question))
        for datasource in query.datasources:
            display_datasource(datasource)
    elif 'generated_sql' in resp:
        # 生成されたSQLを展開可能なブロックで表示
        with st.expander("**SQL generated:**"):
            st.code(resp.generated_sql, language="sql")
    elif 'result' in resp:
        # 取得したデータをDataFrameとして表示
        st.markdown('**Data retrieved:**')

        # レスポンスからフィールド名を取得
        fields = [field.name for field in resp.result.schema.fields]
        # データを辞書形式に変換（カラム名: 値のリスト）
        d = {}
        for el in resp.result.data:
            for field in fields:
                if field in d:
                    d[field].append(el[field])
                else:
                    d[field] = [el[field]]

        # DataFrameを作成して表示
        df = pd.DataFrame(d)

        st.dataframe(df)
        # 後で参照できるようにセッション状態に保存
        st.session_state.lastDataFrame = df


def handle_chart_response(resp):
    """
    チャートレスポンスを表示する

    Vega-Lite形式のチャート設定をAltairで描画
    """
    def _convert(v):
        """
        protoオブジェクトをPythonのネイティブ型に再帰的に変換する

        MapComposite → dict、RepeatedComposite → list、その他 → MessageToDict
        """
        if isinstance(v, proto.marshal.collections.maps.MapComposite):
            return {k: _convert(v) for k, v in v.items()}
        elif isinstance(v, proto.marshal.collections.RepeatedComposite):
            return [_convert(el) for el in v]
        elif isinstance(v, (int, float, str, bool)):
            return v
        else:
            return MessageToDict(v)

    if 'query' in resp:
        # クエリの指示を表示
        st.markdown(resp.query.instructions)
    elif 'result' in resp:
        # チャートを描画
        # 注: st.altair_chartの問題回避のためvega_lite_chartを使用
        # 参考: https://github.com/streamlit/streamlit/issues/6269
        # TODO: 上記issueが解決されたらst.altair_chartに切り替え
        chart = alt.Chart.from_dict(_convert(resp.result.vega_config))
        st.vega_lite_chart(json.loads(chart.to_json()))


def show_message(msg):
    """
    メッセージをタイプに応じて適切に表示する

    対応タイプ:
    - text: テキストレスポンス
    - schema: スキーマ情報
    - data: データテーブル
    - chart: チャート/グラフ
    """
    m = msg.system_message
    if 'text' in m:
        handle_text_response(getattr(m, 'text'))
    elif 'schema' in m:
        handle_schema_response(getattr(m, 'schema'))
    elif 'data' in m:
        handle_data_response(getattr(m, 'data'))
    elif 'chart' in m:
        handle_chart_response(getattr(m, 'chart'))
