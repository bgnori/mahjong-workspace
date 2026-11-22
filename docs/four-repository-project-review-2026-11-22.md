# 4リポジトリ構成のプロジェクトレビュー

レビュー日: 2026-11-22

## 対象と結論

このプロジェクトは、次の4つの独立したGitリポジトリから構成されています。

| 役割 | リポジトリ | レビュー対象HEAD |
|---|---|---|
| Workspace、Dev Container、横断資料 | `mahjong` | `75bc964bcf8d502e0b3f191073de3229636ef29a` |
| 共有Leanドメイン定義 | `mahjong-domain-core` | `53b361b8eae2850ef15972393887d51c518c1b0d` |
| ShantenのLean形式化とGo契約 | `mahjong-shanten-calculation` | `be918559edc584102d381e9d5a3f6f81324233f8` |
| 待ち分類のLean形式化とGo実装 | `mahjong-wait-classification` | `072d116cae1b1cf99a7172aef0e81eebcb4490d3` |

対象はリポジトリ境界、共有ドメインの責務、依存・CI連携、利用者向け文書です。個々の証明やアルゴリズムの網羅的な正当性監査ではありません。

**総評:** Coreが共通の「what」を持ち、Shantenと待ち分類がそれぞれの「how」を持つ分割は明確です。Leanの共有型を各consumerが直接使い、容量規則や固定槓などの境界も区別されています。CIにもCoreとconsumer間の互換性検査があります。設計を妨げる重大な構造問題は見つかりませんでした。

対応を勧める所見は、待ち分類リポジトリ自身のGoテスト不足と、workspace資料から独立リポジトリへのリンク切れです。workspace方式についてはレビュー後にガイドを親フォルダー方式へ統一しました。

## 所見

### P2 — 待ち分類リポジトリのCIがGo実装を検査しない

待ち分類の[CI workflow](https://github.com/bgnori/mahjong-wait-classification/blob/072d116cae1b1cf99a7172aef0e81eebcb4490d3/.github/workflows/checks.yml)はLeanのビルド・回帰テストを実行しますが、GoジョブやGoテストの実行はありません。一方、同リポジトリには[Go分類器のテスト](https://github.com/bgnori/mahjong-wait-classification/blob/072d116cae1b1cf99a7172aef0e81eebcb4490d3/mahjong/classifier_test.go)があります。GoテストはShanten側の[共有ドメインCI](https://github.com/bgnori/mahjong-shanten-calculation/blob/be918559edc584102d381e9d5a3f6f81324233f8/.github/workflows/checks.yml#L144)から待ち分類の`main`に対して実行されますが、待ち分類のPRブランチ自体の変更をそのPR上で検証するものではありません。

**影響:** Lean仕様とGoポートの不一致や、Go単体の回帰を待ち分類リポジトリのPRで検出できない可能性があります。

**推奨:** 待ち分類自身のworkflowに`go test ./...`を追加します。Goの静的検査も他の契約リポジトリと揃えるなら`go vet ./...`も追加します。

### P2 — workspace資料のリポジトリ間リンクをGitHub URLへ修正（対応済み）

レビュー時点では、横断資料の例として[語彙移行状況](./vocabulary-adapter-status.md)、[共有ドメイン調査](./shared-domain-w6-investigation-2026-11-22.md)、[Shanten抽出計画](./shanten-core-extraction-plan-2026-11-22.md)、および[履歴資料](./vocabulary-adapter-status-2026-11-20-archive.md)が、兄弟リポジトリへの相対リンクを含んでいました。workspaceリポジトリは兄弟ディレクトリを`.gitignore`で除外しているため、GitHub上ではリンク先を解決できませんでした。

**影響:** 横断資料から実装・正本の用語集へ移動できず、ローカル表示と公開表示で文書の有用性が変わります。

**対応:** すべてのリポジトリ間リンクをGitHub URLへ変更しました。現行資料は`main`を参照し、履歴資料は各リポジトリの該当時点のコミットに固定しました。履歴資料の用語集リンクは、そのファイルを含むコミットを参照します。リンク先が指定コミットに存在することも検査しました。

### P3 — 親フォルダー方式を維持し、ガイドの説明を統一（対応済み）

[レビュー時点の共有workspaceガイド](https://github.com/bgnori/mahjong-domain-core/blob/53b361b8eae2850ef15972393887d51c518c1b0d/docs/SHARED_WORKSPACE.md)はmulti-rootと説明していましたが、[`mahjong.code-workspace`](../mahjong.code-workspace)は`"."`を1つのfolderとして開く親フォルダー方式です。3つのプロジェクトを兄弟ディレクトリに置く現在の構成は、相対path依存を保ち、各Gitリポジトリの独立性も損なわないため、multi-root化は不要と判断しました。Coreのガイドを実際の設定に合わせ、親フォルダーを1つのworkspace folderとして開く構成だと明記しました。

**推奨:** 親フォルダー方式を維持します。個別workspace rootが必要な設定やタスクが生じた場合にのみ、multi-root化を再検討します。

## 横断評価と残るトレードオフ

- **責務分担:** Coreは牌種、表現、容量、標準形の共有定義を提供し、待ち分類は列挙・分類を、Shantenは探索・評価を担います。Goの固定済み`Meld`契約とLeanの`MentsuCandidate`を別概念として保つ判断も、用語資料と整合しています。
- **ドメイン境界:** 1牌種4枚の規則をCoreに置きつつ、固定牌を含めて何を数えるかはconsumer側に残しています。Pair、手牌中の4枚、固定Kan、特殊形の意味を無理に同一化していません。
- **依存・CI:** consumerのLake設定は兄弟Coreへのpath dependencyを使います。CIはCore変更時にconsumerの`main`を検査し、consumer変更時にもCoreの`main`を検査する構成です。検証したコミットSHAもCI summaryに記録されます。これは変更追従を速める一方、`main`の組合せが時間とともに変わる運用です。資料に記載された移行期の方針として妥当ですが、安定化後に検証済みSHAへ固定する移行条件は継続管理が必要です。
- **未完了の確認:** 既存の移行資料は、代表処理の読みやすさに関する人手確認を未実施として記録しています。機械検証やビルド成功とは別の確認として残すのが適切です。

## 検証

- `mahjong-shanten-calculation`: `go test ./...`と`go vet ./...`は成功（Goパッケージにテストファイルはありません）。
- `mahjong-wait-classification`: `go test ./...`は成功。
- LeanのCore・consumerビルドは実行を試みましたが、現在のworkspaceでは`.lake`配下の一部ファイル／依存キャッシュが別ユーザー所有で、既存ビルド成果物の更新時にpermission deniedとなりました。これはビルド失敗として扱わず、環境権限のため検証未完了とします。
- 既存の横断資料が参照する兄弟リポジトリは、workspaceリポジトリでGit追跡されておらず、ignore対象であることを確認しました。
