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

対象はリポジトリ境界、共有ドメインの責務、依存・CI連携、利用者向け文書です。個々の証明やアルゴリズムの網羅的な正当性監査ではありません。以下には、追加で確認したコード識別子・語彙の読解性に関する所見も記録します。

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

## コード語彙・命名の追加所見

この節のコード確認対象は、`mahjong-domain-core` `e9dcbbcd51d649b1ad6a5dbd402bf6835992e720`、`mahjong-shanten-calculation` `be918559edc584102d381e9d5a3f6f81324233f8`、`mahjong-wait-classification` `072d116cae1b1cf99a7172aef0e81eebcb4490d3`です。これは上表の構成レビュー対象とは別の、命名・語彙に限った追補です。

### P3 — 待ち核の多義性が、同じ待ち牌に対する複数候補として見えにくい

[WaitDecompositionCode.lean](https://github.com/bgnori/mahjong-wait-classification/blob/072d116cae1b1cf99a7172aef0e81eebcb4490d3/Mahjong/WaitDecompositionCode.lean#L59)の`WaitCore`は、1つの待ち牌と完成面子を除いた成分列の組です。重要なのは`WaitCore`が別名か独立した型かではなく、同じ待ち牌に複数の解釈があるとき、異なる成分列を持つ複数の`WaitCore`として表すことです。`waitCores`の返す`List WaitCore`がその候補集合を表します。

たとえば`1223m`は`2m`待ちを、`2m`を雀頭にする単騎と、`13m`の嵌張＋`22m`の雀頭という2つの核で表します。これは同じ待ち牌が複数回現れても重複ではなく、待ちの多義性を表す重要な概念です。既存の`1234m`の例は異なる待ち牌の例なので、この同一待ち牌に対する複数解釈とは区別して説明する必要があります。

**影響:** 型別名そのものは誤りではありませんが、待ち核を単一の候補として読むのか、複数候補をまとめた集合として読むのかが、名前と概略説明だけでは伝わりにくくなっています。

**推奨:** 麻雀上の意味を説明し、同じ待ち牌に異なる核が得られる`1223m`のようなケースを、`findWaitCores`の結果を確かめる実行可能なLean `example`で示します。`WaitCore`を独立型にするか、待ち牌ごとに候補をまとめる型を導入するかは、その意味を説明した後にAPI上の利点で判断すべきです。型の変更だけを先行させる必要はありません。

**追記（2026-11-23）:** 可約性と病理判定が待ち核集合の一致で定義されていることから、`WaitCore`は不変条件を保証すべきと判断しました。`WaitCore`を`mentsuFree`証拠を持つ独立した構造体にし、一般の待ち分解からは`extractWaitCore`、逆方向は`WaitCore.toWaitDecomposition`による明示変換を要求する形で実装済みです。

### P3 — 公開型名`Hand`だけではリポジトリ間の表現の違いが分からない

この所見の初稿では、待ち分類の`Hand`を物理牌IDの埋め込みを持つ型と説明していました。しかし、その後の移行でTenhou IDは入力境界に隔離され、現行の待ち分類`Hand`もCoreの牌種カウントを保持する形に変わっています。以下は2026-11-23に確認した現行コードに基づく再検討です（Core `ffe7e09b2c8c1c898f0109e5755ad8b1e22bd315`、Shanten `579011dca7609d2198a3594304e7277ed1db3b22`、待ち分類 `d6bb8dc0edcc9b115800c2a1b7c70dae01a79f7e`）。

Shantenの[`Shanten.Hand`](https://github.com/bgnori/mahjong-shanten-calculation/blob/579011dca7609d2198a3594304e7277ed1db3b22/Shanten/Core.lean#L18)は、牌種ごとの`TileCounts`と固定面子数を持つ計算状態です。カウント上限の証拠は型に含めず、`ValidCounts`を別の述語として使います。待ち分類の[`Hand`](https://github.com/bgnori/mahjong-wait-classification/blob/d6bb8dc0edcc9b115800c2a1b7c70dae01a79f7e/Mahjong/Hand.lean#L15)は、同じく`TileCounts`を持ち、面子数に応じた総枚数と4枚上限の証拠を持つ牌姿です。Tenhou IDは[`decodeHand`](https://github.com/bgnori/mahjong-wait-classification/blob/d6bb8dc0edcc9b115800c2a1b7c70dae01a79f7e/Mahjong/TenhouInput.lean#L13)で境界変換され、内部の`Hand`には残りません。

したがって、両者は牌の物理表現が違うのではなく、**同じ牌種カウントを異なる文脈・不変条件で使う型**です。Shantenは固定面子数を使う計算状態を表し、待ち分類は指定した面子手テンパイ形の牌姿を表します。共通化を考える対象は`TileCounts`に基づく手元牌の部分であり、固定面子数、面子手サイズ、総枚数、カウントの妥当性を一つのconsumer非依存な`Hand`へまとめることではありません。

**Core.Handの設計案:** 共通の牌種カウントを持つ手元牌部分を明示するため、Coreに次のような基底型を置く案が最も整合的です。

```lean
structure MahjongDomain.Hand where
  counts : MahjongDomain.TileCounts
```

この`Hand`は、物理牌IDや固定面子の内訳を含まない、牌種カウントによる手元牌表現です。`TileCounts.Valid`は既存のCore規則として利用し、基底型の構築時に必須とはしません。これにより、Shantenの既存計算状態が許容する未検証カウントを表現でき、待ち分類側では必要な妥当性と総枚数の証拠を引き続き強制できます。Core `Hand`自体に固定面子数や`3n+1`の枚数制約を入れると、一方のconsumerの意味を他方へ誤って押し付けるため避けます。

consumer側は独自の意味と保証を保ったまま、この基底型を埋め込む形にします。Shanten側には`fixedMelds`を持つ計算状態、待ち分類側には`mentsuCount`、`counts.Valid`および総枚数の証拠を持つテンパイ牌姿が残ります。公開境界では`Shanten.Hand`と待ち分類の牌姿型のように修飾名を使い、単独の`Hand`を横断APIで曖昧に使わないようにします。Coreの型を導入してもconsumer型を即座に同一型へ置き換えたり、別名だけの互換層を増やしたりしません。

**採用条件と実施順:** この案は設計判断であり、Core `Hand`の実装はまだ行っていません。実装時は、(1)両consumerの公開型がCore基底型を直接埋め込み、重複した`counts`フィールドや変換adapterを持たないこと、(2)固定面子数・面子数・妥当性・総枚数の既存保証を弱めないこと、(3)Tenhou境界、探索・分類の結果および既存の無効入力の扱いを変えないこと、(4)Coreと両consumerのLeanビルド・回帰検査を通し、代表的な利用コードが複雑化しないことを確認します。Leanの型階層を介しても単なるwrapperや変換段数が増えるだけなら、Coreの既存`TileCounts`を共通基盤として維持し、新しい`Core.Hand`は導入しません。

### P3 — `Standard`／`Special`語彙を識別子に使わない（実施済み）

**方針:** 識別子では`Standard`／`Special`を使いません。面子手には`MentsuHand`を使い、七対子・国士無双には各形の名前を明記します。

**対応:** Coreの型を`MentsuHandDecomposition`／`MentsuHandCompletion`へ、待ち分類の述語を`IsMentsuHandAgari`へ改名し、関連する定理・証明検査・仕様参照も揃えました。Shantenの上限・牌数定数、待ち導出型も面子手を表す名前へ変更しました。七対子と国士無双の式・容量付きAPIを含むモジュールは[`SevenPairsAndThirteenOrphans.lean`](https://github.com/bgnori/mahjong-shanten-calculation/blob/main/Shanten/SevenPairsAndThirteenOrphans.lean)と[`Capacity/SevenPairsAndThirteenOrphans.lean`](https://github.com/bgnori/mahjong-shanten-calculation/blob/main/Shanten/Capacity/SevenPairsAndThirteenOrphans.lean)に改名し、importと現行案内を更新しました。公開APIに互換aliasは設けず、計算・証明の意味は変更していません。

このP3とは独立する固定槓の用例`specialKanStanding`は、以前の対応で`standingHandWithOneFixedKan`へ改名済みです。

### P3 — `threeMeldStanding`は名詞の結び付きが分かりにくい（対応済み）

[Capacity/Examples.lean](https://github.com/bgnori/mahjong-shanten-calculation/blob/be918559edc584102d381e9d5a3f6f81324233f8/Shanten/Capacity/Examples.lean#L132)にあった`threeMeldStanding`は、`Hand`の`fixedMelds`が3の例でした。`threeMeld`が固定面子数なのか手牌内の面子数なのか、また`standing`とどう結び付くのかが名前だけでは分かりませんでした。

**対応:** 固定面子を3つ持つ手であることが分かる`handWithThreeFixedMelds`へ改名しました。

### P3 — `MahjongComputations.Common`が異なる責務を一つにまとめている

[Common.lean](https://github.com/bgnori/mahjong-wait-classification/blob/072d116cae1b1cf99a7172aef0e81eebcb4490d3/MahjongComputations/Common.lean#L16)には牌列挙、和了分解のグループ化、待ち核キャッシュと可約性、病理分類、分解関係、表示整形までが置かれています。`Common`は「何の共通処理か」を示さず、目的の宣言を探すにはファイル内容を広く読む必要があります。

**推奨:** 次に整理する機会に、`WaitCompletionGrouping`、`WaitCoreReduction`、`WaitPathology`、`WaitDecompositionReporting`など責務を表すモジュールへ分割します。機械的な一括改名より、実際に共有される関数群を基準に分けるのが安全です。

なお、待ち分類の`WinningPartitionSpec`は牌列と列挙された構成部品の仕様、Coreの`MentsuHandCompletion`はカウントに一致する分解証人の仕様です。対応定理で接続されていますが、表現と用途が異なるため、同じ概念の重複として統合するより、それぞれの境界と変換を維持するのが適切です。

## 検証

- `mahjong-shanten-calculation`: `go test ./...`と`go vet ./...`は成功（Goパッケージにテストファイルはありません）。
- `mahjong-wait-classification`: `go test ./...`は成功。
- LeanのCore・consumerビルドは実行を試みましたが、現在のworkspaceでは`.lake`配下の一部ファイル／依存キャッシュが別ユーザー所有で、既存ビルド成果物の更新時にpermission deniedとなりました。これはビルド失敗として扱わず、環境権限のため検証未完了とします。
- 既存の横断資料が参照する兄弟リポジトリは、workspaceリポジトリでGit追跡されておらず、ignore対象であることを確認しました。
