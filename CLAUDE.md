# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Google Conversational Analytics API向けのStreamlitベースのクイックスタートアプリ（分析くん）。データエージェントを通じてBigQueryやLookerのデータソースに自然言語でクエリを実行できる。

## 開発コマンド

```bash
# 依存関係のインストール
pip install -r requirements.txt

# ローカルでアプリを実行
streamlit run app.py

# Dockerで実行
docker build -t data-analytics .
docker run -p 8501:8501 data-analytics
```

アプリは http://localhost:8501 で起動する

## 設定

シークレットは `.streamlit/secrets.toml` で設定:
```toml
[cloud]
project_id = "jambo-data-science"
```

## アーキテクチャ

### コアコンポーネント

- **app.py**: メインエントリーポイント。Streamlitページ設定とAgents/Chat間のナビゲーション
- **state.py**: `st.session_state`を使ったグローバル状態管理。APIクライアント（`DataAgentServiceClient`、`DataChatServiceClient`）の初期化、エージェント・会話・メッセージの管理

### ページモジュール (`app_pages/`)

- **agents.py**: データエージェントのCRUD操作。BigQueryテーブルとLooker exploreをデータソースとしてサポート
- **chat.py**: マルチターンチャットUI。エージェント選択、会話履歴、レスポンス表示

### ユーティリティ (`utils/`)

- **agents.py**: 時間フォーマット用ヘルパー（`get_time_delta_string`）
- **chat.py**: メッセージタイプ別のレスポンスハンドラー（テキスト、スキーマ、データテーブル、チャート）。チャート描画にAltairを使用

### API連携

`google-cloud-geminidataanalytics` SDKを使用:
- `geminidataanalytics.DataAgentServiceClient`: エージェントのCRUD
- `geminidataanalytics.DataChatServiceClient`: 会話とチャット

### データフロー

1. `state.py`の状態初期化で既存のエージェントと会話を取得
2. チャットリクエストは`DataChatServiceClient.chat()`でストリーミングレスポンスを取得
3. レスポンスは`utils/chat.py`の`show_message()`でメッセージタイプ（text/schema/data/chart）に応じて描画
