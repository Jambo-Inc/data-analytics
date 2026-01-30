実装プロンプト（ca-api-quickstarts 改造）

あなたは looker-open-source/ca-api-quickstarts を改造して、BigQueryをデータソースにした会話分析（Conversational Analytics API）を Looker無しで実用化する。目的は次の3点を実装すること：

**Agents画面で「複数テーブル登録 + テンプレ authored context」**を作れるようにする（最重要）

Chat画面でJST/定義/制限を強制し、特に chat_log のデータ爆発（クエリスキャン・行数・トークン）を防ぐ

表示にSQL/参照テーブルを出すことで、監査可能・信頼できるUIにする

重要な前提

Lookerは使わない。BigQueryのみ。

CA API（Conversational Analytics API / Data Agent）を利用し、Authored context（テーブル説明・同義語・例SQL・関係性）で精度を担保する。

リポジトリの既存構造（Streamlitの pages 構成、既存の agent作成/会話送信の流れ）は活かす。

1) Agents画面：複数テーブル登録 + テンプレcontext
   1-1. UI要件（Agents画面）

app_pages/agents.py（または該当するAgents作成ページ）を拡張し、BigQuery data source の入力を「単一テーブル」から「複数テーブル」に変更する。

入力UI：

bq_project_id（必須）

dataset_id（必須）

table references（複数）：

テーブル名を複数行で追加/削除できる UI（例：purchase_log, point_log, chat_log）

内部的には BigQueryTableReference（または同等）を配列で保持する

テンプレ authored context：

contexts/ ディレクトリを新設（なければ）

contexts/jambo_default.yaml のようなテンプレ YAML を追加

Agents画面で「テンプレ選択（dropdown）」→「読み込み」→「編集（テキストエリア）」できる

YAMLの内容を agent 作成時に利用する

1-2. Authored context の構造（テンプレの想定）

テンプレ YAML は最低限以下を含む（名称は実装に合わせてよいが、意図は維持）：

system_preamble（固定前提：JST、定義、出力制限）

tables（各テーブルの説明・主要カラム・同義語）

relationships（JOINキー・粒度）

example_queries（自然文→SQLの例、特にJOINや日付条件）

実装方針：

agent作成時に、CA APIの Data Agent の “authored context” としてこのYAMLを反映する

可能なら「テーブル参照（複数）」も authored context と整合するようにする（＝許可テーブルのホワイトリスト）

1-3. 受け入れ条件（Agents）

Agents作成で、BigQueryの複数テーブルが登録できること

テンプレ YAML を選んで読み込み・編集でき、保存/作成時に反映されること

既存の単一テーブル前提コードが残っていても、UI操作で複数登録が主経路になること

2) Chat画面：JST/定義/制限を強制して chat_log 爆発を防ぐ
   2-1. 強制ルール（必須）

app_pages/chat.py（またはチャット送信ロジック）に、送信前に 必ず前提ルールを組み込む。

JST固定：

「昨日」等の相対日時は JST で解釈

定義固定：

例：「課金＝net_revenue」「上位＝降順」など（テンプレから読める形でもよい）

chat_log制限（最重要）：

chat_log を使う質問は必ず 期間を絞る・件数を絞る・対象ユーザーを絞る

例：直近7日、上位3相手、最大100メッセージ、など

制限が満たせない質問（例：期間指定なしで全件）は、まず「期間を指定して」等のガイド応答に誘導するか、内部でデフォルト制限を付与する

2-2. 実装方式（推奨）

以下のどちらか（または両方）で強制する：

方式A：会話の最初に system/preamble メッセージを注入

会話作成時（new conversation）に、最初のユーザーメッセージの前に「固定前提」を挿入

方式B：各ターン送信時に guardrail テキストを先頭に付与

ユーザーメッセージを送る直前に、固定の制約文を prepend する

テンプレ YAML の system_preamble を使って、Agentsごとにルールを切り替えられる設計が望ましい。

2-3. 受け入れ条件（Chat）

「昨日」を含む質問を投げても、JSTで処理される前提が必ず入る

chat_log を参照する回答で、必ず期間/件数/対象の絞り込みが働く（SQLに反映される or ガイド応答になる）

既存の会話機能（conversation list / resume）が壊れない

3) 表示：SQL / 参照テーブルを出して信頼性UP
   3-1. UI表示要件

チャットの各回答に対し、可能な範囲で以下を表示する：

生成/実行されたSQL（折りたたみ可能 UI：expander）

参照したテーブル一覧（SQLからパースできるならパース結果、無理ならレスポンス内メタデータ）

結果の表（上位N件のみ）：N=20などで固定（UI負荷を避ける）

3-2. 実装メモ

既存の show_message() やチャット描画ユーティリティ（utils/chat.py 相当）があるならそこを拡張する

CA APIレスポンスに SQL/steps/metadata が含まれる場合はそれを優先して表示

SQLが取得できない場合でも、最低限「参照テーブル（推定）」だけでも出す

3-3. 受け入れ条件（表示）

回答ごとに「SQLを表示」セクションが出る（取得できた場合）

参照テーブルが確認できる

結果が大きすぎる場合でもUIが破綻しない（上位N件制限）

コード変更の指示（どこを触るか）

app_pages/agents.py：複数テーブル入力 + contextテンプレ選択/編集 + agent作成に反映

app_pages/chat.py：system_preamble/guardrails 注入 + chat_log 制限

utils/chat.py（または描画ロジック）：SQL/テーブル/結果のexpander表示

contexts/：テンプレ YAML を追加（少なくとも1つ）

必要なら utils/context_loader.py のような小さなローダを追加してよい

テンプレ YAML（例：contexts/jambo_default.yaml）に最低限入れる内容（サンプル）

system_preamble：

「タイムゾーンはJST」

「個人情報は出さない」

「chat_log は必ず期間（デフォルト7日）・最大件数（デフォルト100）・対象ユーザーを絞る」

tables：

marts.purchase_log：課金ログ、amount, purchased_at, user_id

curated.point_log：相互作用ログ、user_id, partner_id, interaction_type, created_at

curated.chat_log：会話ログ、user_id, partner_id, message, sent_at

relationships：

purchase_log.user_id = point_log.user_id

point_log.partner_id = chat_log.partner_id（など仮でOK）

example_queries：

「昨日最も課金したユーザーを10名」→ SQL

「そのユーザーがよくやりとりする相手TOP3」→ SQL

「対象ユーザー×相手TOP3の直近7日チャット要約用抽出」→ SQL

※ カラム名が未確定でも、実装はテンプレを差し替えられる構造にしておくこと。

完了時に提出してほしいもの

変更したファイル一覧

主要な差分（Agents入力、Chatガードレール、SQL表示）の説明

ローカル実行手順（環境変数や認証が必要ならそれも）

画面上での動作確認手順（どう入力し、どう見えるか）