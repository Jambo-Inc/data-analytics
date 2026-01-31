"""
チャットレスポンス表示用ユーティリティ
メッセージタイプ（テキスト、スキーマ、データ、チャート）に応じた描画処理を提供する

参考: https://cloud.google.com/gemini/docs/conversational-analytics-api/build-agent-sdk#define_helper_functions
"""
import pandas as pd
import json
import re
import altair as alt
from typing import List

import proto
from google.protobuf.json_format import MessageToDict

import streamlit as st

# 表示行数の上限
MAX_DISPLAY_ROWS = 20


def format_user_data_text(text: str) -> str:
    """
    ユーザーデータを含むテキストを見やすく整形する

    user_id:で始まる複数ユーザーの情報を改行で区切り、
    各種類の回数を箇条書き形式に整形する
    """
    # user_id: パターンで分割（最初の空マッチを除去）
    user_pattern = r'(user_id:\s*[a-f0-9]+)'
    parts = re.split(user_pattern, text)

    # user_id:パターンが見つからない場合はそのまま返す
    if len(parts) <= 1:
        return text

    formatted_lines = []
    i = 0
    # 最初の部分（user_id:より前のテキスト）
    if parts[0].strip():
        formatted_lines.append(parts[0].strip())
        formatted_lines.append("")
    i = 1

    while i < len(parts):
        if i + 1 < len(parts):
            user_id = parts[i].strip()
            data = parts[i + 1].strip()

            # 回数データを「:」と「回」で分割して箇条書きに
            # パターン: "種類名: N回" を検出
            items = re.findall(r'([^:]+?):\s*(\d+)回', data)

            if items:
                formatted_lines.append(f"**{user_id}**")
                for item_name, count in items:
                    item_name = item_name.strip()
                    if item_name:
                        formatted_lines.append(f"  - {item_name}: {count}回")
                formatted_lines.append("")
            else:
                # パターンにマッチしない場合はそのまま
                formatted_lines.append(f"**{user_id}** {data}")
                formatted_lines.append("")
            i += 2
        else:
            formatted_lines.append(parts[i])
            i += 1

    return "\n".join(formatted_lines)


def handle_text_response(resp):
    """
    テキストレスポンスを表示する
    複数のパーツがある場合は結合してMarkdownで表示
    ユーザーデータを含む場合は見やすく整形する
    """
    parts = getattr(resp, 'parts')
    text = ''.join(parts)

    # user_id:を含む場合は整形
    if 'user_id:' in text:
        text = format_user_data_text(text)

    st.markdown(text)


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


def extract_referenced_tables(sql: str) -> List[str]:
    """
    SQLからFROM/JOIN句のテーブル名を抽出する

    引数:
        sql: 解析対象のSQL文字列

    戻り値:
        参照されているテーブル名のリスト（ソート済み、重複なし）
    """
    if not sql:
        return []
    tables = set()
    # FROM句からテーブル名を抽出（バッククォート対応）
    from_matches = re.findall(
        r'FROM\s+`?([a-zA-Z0-9_\-]+(?:\.[a-zA-Z0-9_\-]+){0,2})`?',
        sql,
        re.IGNORECASE
    )
    tables.update(from_matches)
    # JOIN句からテーブル名を抽出（バッククォート対応）
    join_matches = re.findall(
        r'JOIN\s+`?([a-zA-Z0-9_\-]+(?:\.[a-zA-Z0-9_\-]+){0,2})`?',
        sql,
        re.IGNORECASE
    )
    tables.update(join_matches)
    return sorted(list(tables))


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
        sql = resp.generated_sql
        # 参照テーブルを表示
        referenced_tables = extract_referenced_tables(sql)
        if referenced_tables:
            st.markdown("**参照テーブル:** " + ", ".join(f"`{t}`" for t in referenced_tables))
        # 生成されたSQLを展開可能なブロックで表示
        with st.expander("**SQL generated:**"):
            st.code(sql, language="sql")
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
        total_rows = len(df)

        # 行数が上限を超える場合は制限して表示
        if total_rows > MAX_DISPLAY_ROWS:
            display_df = df.head(MAX_DISPLAY_ROWS)
            st.info(f"表示: {MAX_DISPLAY_ROWS}件 / 全{total_rows}件")
        else:
            display_df = df

        st.dataframe(display_df)

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
