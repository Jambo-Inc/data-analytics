"""
エージェント関連のユーティリティ関数
"""
from datetime import datetime, timezone


def get_time_delta_string(past_time: datetime, no_change_str: str) -> str:
    """
    過去の時刻から現在までの経過時間を人間が読みやすい形式で返す

    例: "2 days, 3 hours, 15 minutes ago"

    引数:
        past_time: 比較する過去の時刻（UTC）
        no_change_str: 時間差がほぼゼロの場合に返す文字列（例: "Just created"）

    戻り値:
        "X days, Y hours, Z minutes ago" 形式の文字列
        またはno_change_str（差分がない場合）
    """
    # 現在時刻との差分を計算
    current_time = datetime.now(timezone.utc)
    time_difference = current_time - past_time

    # 日、時間、分、秒に分解
    days = time_difference.days
    hours, remainder = divmod(time_difference.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # 各単位を人間が読みやすい形式に変換（複数形対応）
    parts = []
    if days:
        parts.append(f"{days} day{'s' if days > 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    if seconds:
        parts.append(f"{seconds} second{'s' if seconds > 1 else ''}")

    # 時間差がほぼゼロの場合はデフォルト文字列を返す
    if not parts:
        return no_change_str

    return ", ".join(parts) + " ago"
