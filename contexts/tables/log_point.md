## テーブル情報
- ポイント付与・消費ログテーブル

## カラム説明

| カラム名 | 説明 |
|----------|------|
| user_id | ユーザーID |
| type | アクションタイプ（下記参照） |
| tradable_point | 換金可能ポイント変動量 |
| untradable_point | 換金不可ポイント変動量 |
| sales_amount | 売上金額 |
| before_tradable_point | 変動前の換金可能ポイント |
| after_tradable_point | 変動後の換金可能ポイント |
| before_untradable_point | 変動前の換金不可ポイント |
| after_untradable_point | 変動後の換金不可ポイント |
| time | 記録日時 |
| original_time | 元の日時 |
| partner_id | 相手ユーザーID |
| provider_id | プロバイダーID |
| ip | IPアドレス |
| application_id | アプリケーションID（userテーブル参照） |
| trader_user_id | 取引相手ユーザーID |
| total_point | 合計ポイント |
| total_consume_point | 合計消費ポイント |
| total_earned_point | 合計獲得ポイント |
| precedent_id | 先行ID |

## カラム変換ルール

### type（アクションタイプ）

| ID | アクション名 | 説明 |
|----|-------------|------|
| 1 | register | 新規登録 |
| 2 | daily_bonus | デイリーボーナス |
| 3 | invite_friend | 友達招待 |
| 4 | cash | 課金 |
| 5 | unlock_backstage_bonus | 裏プロフ解放ボーナス |
| 6 | who_favorited_me | お気に入りされた |
| 7 | who_check_me_out | 足あと確認 |
| 8 | unlock_backstage | 裏プロフ解放 |
| 9 | save_image | 画像保存 |
| 10 | wink_bomb | ウィンク爆弾 |
| 11 | send_gift | ギフト送信 |
| 12 | online_alert | オンライン通知 |
| 13 | bid | 入札 |
| 14 | admistrator | 運営付与 |
| 15 | voice_call | 音声通話 |
| 16 | video_call | ビデオ通話 |
| 17 | chat | チャット |
| 18 | buy_sticker | スタンプ購入 |
| 19 | wink | ウィンク |
| 20 | view_image | 画像閲覧 |
| 21 | view_image_bonus | 画像閲覧ボーナス |
| 22 | receive_gift | ギフト受信 |
| 23 | send_sticker | スタンプ送信 |
| 24 | receive_sticker | スタンプ受信 |
| 25 | save_image_bonus | 画像保存ボーナス |
| 26 | advertsement | 広告 |
| 27 | add_buzz_bonus | つぶやきボーナス |
| 28 | add_looking_for | 探している人を追加 |
| 29 | add_about_me | 自己紹介を追加 |
| 30 | add_avatar | アバター追加 |
| 31 | add_relationship | 交際ステータス追加 |
| 32 | add_body_type | 体型追加 |
| 33 | add_height | 身長追加 |
| 34 | add_ethnicity | 人種追加 |
| 35 | add_interes | 興味追加 |
| 36 | receive_wink | ウィンク受信 |
| 37 | receive_chat | チャット受信 |
| 38 | trade_point_to_money | ポイント換金 |
| 39 | report_buzz | つぶやき通報 |
| 40 | delete_buzz | つぶやき削除 |
| 41 | get_free_point | 無料ポイント取得 |
| 42 | add_age | 年齢追加 |
| 43 | add_email | メール追加 |
| 44 | comment_buzz | つぶやきコメント |
| 45 | comment_bonus | コメントボーナス |
| 46 | login_bonus_day_1 | ログインボーナス1日目 |
| 47 | login_bonus_day_2 | ログインボーナス2日目 |
| 48 | login_bonus_day_3 | ログインボーナス3日目 |
| 49 | login_bonus_day_4 | ログインボーナス4日目 |
| 50 | login_bonus_day_5 | ログインボーナス5日目 |
| 51 | login_bonus_day_6 | ログインボーナス6日目 |
| 52 | login_bonus_day_7 | ログインボーナス7日目 |
| 53 | purchase_login_bonus_day_1 | 課金ログインボーナス1日目 |
| 54 | purchase_login_bonus_day_2 | 課金ログインボーナス2日目 |
| 55 | purchase_login_bonus_day_3 | 課金ログインボーナス3日目 |
| 56 | purchase_login_bonus_day_4 | 課金ログインボーナス4日目 |
| 57 | purchase_login_bonus_day_5 | 課金ログインボーナス5日目 |
| 58 | purchase_login_bonus_day_6 | 課金ログインボーナス6日目 |
| 59 | purchase_login_bonus_day_7 | 課金ログインボーナス7日目 |
| 60 | send_gift_sticker | ギフトスタンプ送信 |
| 61 | receive_gift_sticker | ギフトスタンプ受信 |
| 62 | invite_male_friend | 男性友達招待 |
| 63 | register_email_bonus | メール登録ボーナス |
| 64 | comeback_friend | カムバック友達 |
| 68 | pick_up_like | ピックアップいいね |
| 70 | start_dash_favorite | スタートダッシュお気に入り |
| 71 | add_point_back_point | ポイントバック |
| 72 | add_event_mission_point | イベントミッションポイント |
| 73 | add_special_bonus | 特別ボーナス |
| 74 | start_dash_chat | スタートダッシュチャット |
| 75 | view_video | 動画閲覧 |
| 76 | view_video_bonus | 動画閲覧ボーナス |
| 77 | add_marriage_history | 結婚歴追加 |
| 78 | add_showing_face_status | 顔出し状況追加 |
| 79 | add_step_to_call | 通話までのステップ追加 |
| 80 | add_personalities | 性格追加 |
| 81 | add_talk_theme | 話題追加 |
| 82 | merge_increase_point | 統合によるポイント増加 |
| 83 | merge_decrease_point | 統合によるポイント減少 |
| 84 | double_daily_bonus | デイリーボーナス2倍 |
| 85 | achieved_thirty_days | 30日達成 |
| 86 | achieved_sixty_days | 60日達成 |
| 87 | achieved_ninety_days | 90日達成 |
| 88 | trade_point_bonus | 換金ボーナス |
| 89 | add_receive_like_point_back | いいね受信ポイントバック |
| 90 | add_receive_miu_spu_point_back | Miu SPUポイントバック |
| 91 | extra_daily_bonus | 追加デイリーボーナス |
| 92 | add_first_daily_call_bonus_point | 初回デイリー通話ボーナス |
| 93 | add_point_if_wc_shared_sns | WC SNSシェアボーナス |
| 94 | add_point_if_calendar_shared_sns | カレンダーSNSシェアボーナス |
| 95 | add_mail_point_back | メールポイントバック |
| 96 | add_video_call_point_back | ビデオ通話ポイントバック |
| 97 | add_roulette_campaign_point | ルーレットキャンペーンポイント |
| 98 | add_free_video_call_campaign_point | 無料ビデオ通話キャンペーンポイント |
| 99 | add_video_call_high_point_back | ビデオ通話高額ポイントバック |
| 100 | add_first_point_of_video_call_double_point_back | ビデオ通話2倍ポイントバック（1回目） |
| 101 | add_second_point_of_video_call_double_point_back | ビデオ通話2倍ポイントバック（2回目） |
| 102 | add_upload_story_campaign_point | ストーリー投稿キャンペーンポイント |
| 103 | add_scratch_campaign_point | スクラッチキャンペーンポイント |
| 104 | pay_video_lovense_menu_point_for_first_apps | Lovenseビデオメニュー支払い（初回アプリ） |
| 105 | add_video_lovense_menu_point_for_first_apps | Lovenseビデオメニュー付与（初回アプリ） |
| 106 | add_unlimited_roulette_campaign_point | 無制限ルーレットキャンペーンポイント |
| 107 | add_unlimited_roulette_campaign_point_for_female | 無制限ルーレットキャンペーンポイント（女性） |
| 108 | add_free_lovense_campaign_point | 無料Lovenseキャンペーンポイント |
| 109 | sixth_apps_daily_bonus | 6thアプリデイリーボーナス |
| 110 | add_percentage_point_from_revenue | 売上からのパーセンテージポイント |
| 152 | add_income_bonus | 収入ボーナス |
| 200 | daily_mission_male_call | デイリーミッション（男性通話） |
| 201 | daily_mission_male_call_purchased | デイリーミッション（男性通話・課金） |
| 202 | daily_mission_male_chat | デイリーミッション（男性チャット） |
| 203 | daily_mission_male_chat_purchased | デイリーミッション（男性チャット・課金） |
| 204 | daily_mission_female_call | デイリーミッション（女性通話） |
| 205 | daily_mission_female_chat | デイリーミッション（女性チャット） |
| 206 | daily_mission_male_board_message | デイリーミッション（男性掲示板） |
| 207 | daily_mission_male_like | デイリーミッション（男性いいね） |
| 209 | add_2nd_voice_point | 2nd音声通話ポイント付与 |
| 210 | decrease_live_chat_point | ライブチャットポイント消費 |
| 211 | add_live_chat_point | ライブ配信ポイント付与 |
| 212 | add_live_video_point | ライブビデオポイント付与 |
| 213 | decrease_live_video_point | 2ndビデオ通話ポイント消費 |
| 214 | decrease_voice_call_point | 2nd音声通話ポイント消費 |
| 215 | decrease_side_watch_point | のぞきポイント消費 |
| 216 | add_side_watch_point | ライブ配信のぞきポイント付与 |
| 217 | decrease_side_watch_chat_point | のぞきチャットポイント消費 |
| 218 | add_side_watch_chat_point | ライブ配信のぞきチャットポイント付与 |
| 219 | add_standby_live_chat_point | ライブ配信待機ポイント付与 |
| 220 | add_first_board_point | 初回掲示板ポイント |
| 221 | add_rabbit_bonus_point | うさぎボーナス |
| 222 | send_free_message_from_web | Webからの無料メッセージ送信 |
| 223 | send_free_greeting_message | 挨拶メッセージ送信 |
| 230 | add_pickup_message_point | ピックアップメッセージポイント |
| 231 | exchange_live_chat_point | 2nd女性メッセージ送信 |
| 232 | receive_live_chat | ライブチャット受信 |
| 233 | add_message_rally_mission_a | メッセージラリーミッションA |
| 234 | add_message_rally_mission_b | メッセージラリーミッションB |
| 235 | add_message_rally_mission_c | メッセージラリーミッションC |
| 236 | add_streaming_daily_mission | 配信デイリーミッション |
| 237 | send_live2d_gift_sticker | Live2Dギフトスタンプ送信 |
| 238 | receive_live2d_gift_sticker | Live2Dギフトスタンプ受信 |
| 239 | add_avatar2d_streaming_daily_mission | 2Dアバター配信デイリーミッション |
| 240 | exchange_avatar2d_chat_point | 2Dアバターチャットポイント交換 |
| 250 | add_franc_beginner_mission | Franc初心者ミッション |
| 251 | add_premium_option_apology_point | プレミアムオプションお詫びポイント |
| 252 | exchange_muse_timeline_action_point | Museタイムラインアクションポイント交換 |
| 253 | receive_muse_timeline_action_point | Museタイムラインアクションポイント受信 |
| 254 | male_first_post_timeline_bonus_point | 男性初回タイムライン投稿ボーナス |
| 255 | add_muse_timeline_receive_like_point_back | Museタイムラインいいねポイントバック |
| 256 | add_muse_timeline_consume_point_back | Museタイムライン消費ポイントバック |
| 257 | add_monthly_point_back | 月間ポイントバック |
| 258 | credit | クレジット |
| 259 | add_avatar2d_campaign_point_back | 2Dアバターキャンペーンポイントバック |
| 260 | add_first_voice_call_bonus_point | 初回音声通話ボーナス |
| 261 | add_first_video_call_bonus_point | 初回ビデオ通話ボーナス |
| 262 | add_first_live_chat_call_bonus_point | 初回ライブチャットボーナス |
| 263 | add_first_purchase_reset_campaign_point | 初回課金リセットキャンペーンポイント |
| 264 | add_favorite_point_campaign | お気に入りポイントキャンペーン |
| 270 | add_forth_apps_voice_call_point | 4thアプリ音声通話ポイント付与 |
| 271 | decrease_fourth_apps_voice_call_point | 4thアプリ音声通話ポイント消費 |
| 280 | add_2nd_female_beginner_mission | 2nd女性初心者ミッション |
| 281 | weekly_challenge_bonus | 週間チャレンジボーナス |
| 282 | video_chat_stamp_bonus | ビデオチャットスタンプボーナス |
| 283 | pay_video_chat_menu_point | ビデオチャットメニュー支払い |
| 284 | add_video_menu_bonus | ビデオメニューボーナス |
| 285 | pay_lovense_menu_point | Lovenseメニュー支払い |
| 286 | add_lovense_menu_point | Lovenseメニューポイント付与 |
| 287 | pay_video_lovense_menu_point | Lovenseビデオメニュー支払い |
| 288 | add_video_lovense_menu_point | Lovenseビデオメニューポイント付与 |
| 290 | play_audio | 音声再生 |
| 291 | play_audio_bonus | 音声再生ボーナス |
| 292 | spu_point_back | SPUポイントバック |
| 300 | gokon | 合コン |
| 301 | private_date | プライベートデート |
| 302 | add_first_credit_register_point | 初回クレカ登録ポイント |
| 303 | decrease_third_apps_video_point | 3rdビデオ通話ポイント消費 |
| 304 | add_third_apps_video_point | 3rdビデオ通話ポイント付与 |
| 305 | change_miu_ios_to_mila_point | Miu-iOSからMila移行ポイント |
| 306 | paidy | Paidy決済 |
| 307 | add_5th_female_beginner_mission | 5th女性初心者ミッション |
| 308 | pwa_register_bonus | PWA登録ボーナス |
| 309 | random_match_point_back_bonus | ランダムマッチポイントバックボーナス |
| 310 | notification_permission_bonus | 通知許可ボーナス |
| 311 | sixth_apps_chat | 6thアプリチャット |
| 312 | sixth_apps_video_chat | 6thアプリビデオチャット |
| 313 | sixth_apps_mission_bonus | 6thアプリミッションボーナス |
| 314 | sixth_apps_register | 6thアプリ登録 |
| 315 | fifth_apps_voice_call | 5thアプリ音声通話 |
| 316 | add_step_to_date | デートまでのステップ追加 |
| 317 | add_salary | 年収追加 |
| 318 | add_work_space | 職場追加 |
| 319 | add_academic_background | 学歴追加 |
| 320 | add_brothers | 兄弟追加 |
| 321 | amazon_pay | Amazon Pay |
| 322 | google_pay | Google Pay |
| 323 | apple_pay | Apple Pay |
| 324 | referrer_bonus | 友達紹介ボーナス（紹介者） |
| 325 | referee_bonus | 友達紹介ボーナス（被紹介者） |
| 326 | lovense_mission | Lovenseミッション |
| 327 | male_call_mission | 男性通話ミッション |
| 328 | utage_onboarding_mission | Utageオンボーディングミッション |
| 329 | miu_web_onboarding_mission | Miu Webオンボーディングミッション |
| 330 | add_weekly_point_back | 週間ポイントバック |
| 331 | felea_market_point | フリマポイント |
| 332 | purchase_lovense | Lovense購入 |
| 333 | video_call_mission | ビデオ通話ミッション |
| 334 | restore_male_video_call | 男性ビデオ通話復元 |
| 335 | restore_male_voice_call | 男性音声通話復元 |
| 336 | male_video_chat_mission | 男性ビデオチャットミッション |
| 337 | female_video_chat_mission | 女性ビデオチャットミッション |
| 338 | male_class_bonus | 男性クラスボーナス |
| 339 | restore_male_random_video_call | 男性ランダムビデオ通話復元 |
| 340 | point_rollback | ポイントロールバック |
| 341 | add_review_bonus_point | レビュー投稿ボーナス |
