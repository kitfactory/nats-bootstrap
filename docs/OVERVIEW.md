# docs/OVERVIEW.md

## 現在地
- フェーズ: P0（concept/spec/plan整備 + MVP骨組み）
- 今回スコープ: bootstrap モード（--cluster/--datafolder）とドキュメント/CLI更新
- 参照リンク:
  - concept: `docs/concept.md`
  - spec: `docs/spec.md`
  - architecture: `docs/architecture.md`
  - plan: `docs/plan.md`
  - nats CLI install: `docs/nats_cli_install.md`
  - manual (ja): `manuals/manual_ja.md`
  - manual (en): `manuals/manual_en.md`

## 重要メモ
- 入口は `docs/OVERVIEW.md`、正本は `docs/`。
- レビューゲート: 自己レビュー → ユーザー確認 → 合意で次へ。
- 大きい変更は「提案 → 合意 → 適用」。

## 変更履歴
- 2026-01-29: ドキュメント再作成、MVP骨組みの実装開始。
- 2026-01-29: 既定の設定ファイル検索順を「実行ディレクトリ → ユーザーディレクトリ」に変更。
- 2026-01-29: 設定読み込み優先順を「--config → 実行ディレクトリ → ユーザー」に整理し、`nats-config.json` を .gitignore 対象に追加。
- 2026-01-29: `--config` 指定時の未存在ファイルをエラー扱いに変更。
- 2026-01-29: `--config` をサブコマンドの前後どちらでも指定可能に変更。
- 2026-01-29: doctor にバイナリ解決の優先順表示を追加。
- 2026-01-29: planの順序を機能影響ベースに再整理し、controller実装をcurrentに移動。
- 2026-01-29: controller の仕様（CLI/HTTP/冪等性）を spec に追記。
- 2026-01-29: controller の設計メモを architecture.md に作成。
- 2026-01-29: controller/leave のCLI実装と doctor の疎通チェックを追加。
- 2026-01-29: controller/leave を現物テストで確認。
- 2026-01-29: down/leave の安全方針と I/F を spec に追記。
- 2026-01-29: down/leave の安全実装（confirm/pid）の最小版を追加。
- 2026-01-29: resolve_binary/config/doctor/CLI のテストを追加し実行手順を README に追記。
- 2026-01-29: Windowsサービスの方針/I-F/固定パス仕様を spec に追記。
- 2026-01-29: Windowsサービス install/uninstall/up/doctor を実装しテストを追加。
- 2026-01-29: Windowsサービスの現物テストは権限不足（Access denied）で失敗。
- 2026-01-29: backup/restore の仕様とCLI実装を追加。
- 2026-01-29: backup/restore のテストを追加（nats CLI 未検出を確認）。
- 2026-01-29: Windowsサービスの管理者権限テスト（install/up/doctor/uninstall）完了。
- 2026-01-29: README（日英）と詳細マニュアル（日英）を追加。
- 2026-01-30: 詳細マニュアルの配置を `manuals/` に統一。
- 2026-01-30: README/マニュアルのインストール表記をパッケージ形式に更新し、join（upのエイリアス）を追記。
- 2026-01-30: 詳細マニュアルのクラスタ手順を「最初の1台 → 追加」に更新。
- 2026-01-30: bootstrap モード（--cluster/--seed/--datafolder）を仕様/実装/テストに追加。
- 2026-01-30: README/マニュアルに設定ファイル自動生成の手順を追記。
- 2026-01-30: bootstrap の追加オプション（--listen/--cluster-port/--client-port/--http-port）と seed 既定ポートの説明を追加。
- 2026-01-30: README/マニュアルに bootstrap の売りと nats CLI 必須（backup/restore）を追記。
- 2026-01-30: README 冒頭にキャッチコピーを追加。
- 2026-01-30: README/マニュアルの表現を平易化（同一手順/対称運用の言い換え）。
- 2026-01-30: nats CLI のインストール手順を別文書に分離し参照リンクを追加。
- 2026-01-30: `nats.exe` はCLIでありサーバーは `nats-server.exe` である旨を追記。
- 2026-01-30: マニュアルのFAQに `nats.exe` と `nats-server.exe` の違いを追記。
