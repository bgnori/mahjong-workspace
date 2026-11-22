# ShantenからCoreへの共有機能抽出計画

基準日: 2026-11-22

関連: [共有ドメイン語彙への移行状況と対応計画](./vocabulary-adapter-migration-plan-2026-11-22.md)、
[共有ドメイン語彙とAdapterの現状](./vocabulary-adapter-status.md)、
[SharedDomainW6の調査と今後の整理](./shared-domain-w6-investigation-2026-11-22.md)

## 目的・位置づけ

待ち分類から順子のランク操作や部品の順序付き展開をCoreに置いたように、
Shanten側の定義・操作・定理からも、探索に限定されない麻雀の共通概念を見直す。
既存計画の「Shanten Lean移行完了」は、**当時Coreに存在した牌・面子・表現の
直接利用が完了した**という意味であり、追加抽出の検討を完了したという意味ではない。

Coreは共有ドメインのwhat、consumerは探索・分類などのhowを担う。
現在の利用者がShantenだけであることは、共通概念をCoreに置かない理由とは限らない。
一方、利用箇所が多いことだけでも共有化を正当化しない。対象ごとに意味・前提・
公開したい保証を示し、重複するlocal定義があれば直接利用に切り替えてから削除する。
移行用Adapterや互換aliasは必要な期間だけとし、移行後に残さない。

読みやすさの人手確認は、今回のざっとした確認では判定できないため持ち越す。
機械検証や宣言数の比較を人手確認の代わりにしない。

## 現状と候補

この表は計画時点の候補と判断基準です。実施後の状態は次節を参照してください。

| 優先 | 候補と根拠 | 判断・境界 |
|---|---|---|
| 1 | [Shanten.Core](https://github.com/bgnori/mahjong-shanten-calculation/blob/main/Shanten/Core.lean)の`orphanKinds`、`kokushiKinds`、`orphanTiles`と[ThirteenOrphans](https://github.com/bgnori/mahjong-shanten-calculation/blob/main/Shanten/ThirteenOrphans.lean)の集合一致・13種・牌数の定理。么九牌の集合そのものは特定の探索方法ではない。 | まず、端の数牌と字牌の判定、13牌種、必要なら各牌種1枚の多重集合をCoreに置くことを検討する。現在は定義上の集合と計算用列挙が別にあり、両者の一致を証明している。計算可能性を失わず、同じ集合を正本から得る。国士のシャンテン式、手牌、完成・探索は移さない。 |
| 2 | [Shanten.Exchange](https://github.com/bgnori/mahjong-shanten-calculation/blob/main/Shanten/Exchange.lean)の`countsOfTiles_sum_eq_card`、[MentsuHand.State](https://github.com/bgnori/mahjong-shanten-calculation/blob/main/Shanten/MentsuHand/State.lean)の`meldsTiles_card`。いずれも共有牌種・部品の枚数に関する定理で、`Hand`や探索状態を引数に持たない。 | Coreの`TileCounts.ofMultiset`、`Pair.tiles_card`、`MentsuCandidate.tiles_card`、`MentsuCandidateList.tiles`に対する共有基本則として抽出候補。既存の`pairTiles_card`はCoreの`Pair.tiles_card`の利用箇所を見直し、不要なwrapperを除去する。CoreやMathlibの既存定理と重複しないことを確認する。 |
| 3 | [Shanten.Core](https://github.com/bgnori/mahjong-shanten-calculation/blob/main/Shanten/Core.lean)の`tileCount`、`presentTiles`、`distinctTileCount`、`pairCount`。現在はShantenの`Hand`を受け取るが、計算自体は牌種カウントに依存する。 | `TileCounts`に対する総数・存在牌種・2枚以上の牌種数として切り出す価値を検討する。`pairCount`は**2枚以上ある牌種の数**であり、対子の組数でも七対子の完成判定でもない。具体的な利用と名前・前提を照合し、単なるwrapper追加なら移さない。 |
| 条件付き | [Capacity.Basic](https://github.com/bgnori/mahjong-shanten-calculation/blob/main/Shanten/Capacity/Basic.lean)の`FixedMeld`、`FixedMeld.tiles`、`fixedTiles`、`remainingCapacity`。固定した順子・刻子・槓の占有と残余容量は探索から分離できる可能性がある。 | まず固定面子が表す情報を検討する。現型は完成形か槓かと牌種を保持するが、鳴きの種類・赤牌の同一性は保持しない。Goの固定済み`Meld`や分類の候補型と同一視しない。`4 - occupied`は自然数減算で0に飽和し、過剰占有の検出には別途占有上限が必要。妥当性や利用上の需要を確認できた部分だけを抽出する。 |
| 再検討・保留 | [MentsuHand.Basic](https://github.com/bgnori/mahjong-shanten-calculation/blob/main/Shanten/MentsuHand/Basic.lean)の`Taatsu`、牌展開、完成牌と完成面子。 | 現在の`Taatsu`は対子と隣接2牌だけで嵌張を含まず、両面では完成候補の一方を選ぶ探索用の証人である。[待ち分類](https://github.com/bgnori/mahjong-wait-classification/blob/main/Mahjong/WaitDecompositionCode.lean)の両面・嵌張・辺張などの分類とは同一ではない。共通の不完全部品として何を保証するかを別途設計し、全候補や重複・端の扱いを照合するまでは型や完成選択を移さない。既存計画の「Shanten固有の`Taatsu`は対象外」を見直すための調査候補であり、その変更を先取りしない。 |
| 再検討・保留 | [SevenPairs.Basic](https://github.com/bgnori/mahjong-shanten-calculation/blob/main/Shanten/SevenPairs/Basic.lean)の牌種集合から作る七対子カウント、および国士の牌構成。 | 七対子や国士の**牌構成そのもの**は共有候補だが、完成・合法性・ルール前提の境界は未確定。7種の異なる対子、4枚を2対としない扱い、国士の13種と重複1枚を明示してから検討する。既存の`Completion`のconsumer横断統一・改名は別課題のままとし、特定の完成述語をそのままCoreへ移さない。 |

Shanten側の`Hand`、入力・エラー契約、`ValidHand`、交換・到達可能性、
シャンテン式・距離・探索・DP・分類は、上のように切り出せる共通部分を除いて
Shanten側に残す。待ち分類の物理的`Hand`とShantenのカウント状態を統合しない。
GoはLeanをimportできないため、Goの変更が必要な場合も表現仕様との照合を別途行う。

## 実施結果と保留判断

- **么九牌を抽出:** Coreの`Tile.IsTerminalOrHonor`、計算可能な`orphanKinds`と
  `orphanTiles`を正本とする。旧`kokushiKinds`と同じ13種を列挙し、
  `mem_orphanKinds`で全牌種に対する端牌・字牌判定との一致を証明した。
  集合・多重集合の列挙順は契約しない。国士の完成条件や計算はShantenに残す。
- **基本則を抽出:** Coreに`TileCounts.ofMultiset_sum_eq_card`と
  `MentsuCandidateList.tiles_card`を置き、Shantenは既存の`Pair.tiles_card`を含め
  直接利用する。旧枚数定理と么九牌の重複宣言は削除し、再導入をCIで検査する。
- **`tileCount`等は現状維持:** 現在の利用はShantenの`Hand`を通じた計算で、
  `TileCounts`版を追加しwrapperも残すだけでは公開APIが増える。wrapperを除くには
  手版の利用箇所を切り替える必要があるが、今回共有した枚数定理以上にCoreで
  保証すべき操作・命名の要件は未確定。直接必要とする利用と併せて再検討する。
  `pairCount`は同種4枚でも1牌種と数え、Pairの抽出や完成判定とは異なる。
- **固定牌は保留:** 現型は順子・刻子・槓の形と占有を表すが、鳴きの種類や赤牌の
  同一性を表さない。Goの固定済み`Meld`とは情報が異なる。自然数の
  `4 - occupied`は固定牌だけの過剰占有でも0に飽和し、standingとの合計超過も
  別の上限検証が必要。形・占有を共有する利用と妥当性の境界を明確にしてから再検討する。
- **4枚則はCoreの責務:** 上記の固定牌型の保留とは別に、1牌種4枚という基本ルールは
  Coreを正本とし、物理牌・Int37との整合とconsumerによる直接利用を実施した。
  [W6調査](./shared-domain-w6-investigation-2026-11-22.md)に結果を記録している。
- **搭子は別課題:** 現型は対子と隣接2牌だけで嵌張を含まず、両面では完成候補の
  一方を選ぶ探索用証人である。待ち分類の待ち種別とは一致しない。共通の不完全部品の
  範囲と、両面の複数候補・辺牌・重複を含む保証を設計してから再検討する。
- **特殊形の構成は別課題:** 七対子は7種の異なる対子で、4枚を2対としない。
  国士は13種に重複1枚を加える。構成と合法性・完成条件の境界やルール前提を
  consumer間で確定してから抽出する。`Completion`の横断統一・改名は引き続き保留。

読みやすさの人手確認は未実施のまま持ち越す。

**検証:** 書き込み可能な隔離コピーでCoreの`lake build MahjongDomain`、
Shantenの`lake build`、待ち分類の`lake build Mahjong MahjongTests`、
固定文脈連携の`w6`で`lake build`が通過した。共有基本則と既存のShanten・
連携出口定理の`sorry`不在も確認した。Goのコード・契約は変更していない。
CIがCoreの`main`を参照するため、公開時はCoreを先に反映する。

## 実施順序

### 0. 範囲と意味を確定する

1. 上表の候補ごとに、現行の定義・全利用箇所・前提・CoreやMathlibの既存APIを確認する。
   共有概念、consumer固有の使用方法、単なる実装詳細を分ける。
2. Coreの公開名・計算可能性・順序や重複の契約を決める。特に集合と順序付き列を混同せず、
   么九牌の列挙順を公開仕様にするかどうかを明示する。
3. 条件付き・保留候補は意味や利用上の必要性が確認できなければ移さず、理由と再検討条件を記録する。

**成果:** 抽出対象と非対象、名前、前提と保証の一覧。既存の`Taatsu`や`Completion`の境界を
変える提案は、この段階で既存計画との差分として明示する。

### 1. 么九牌の共有定義を抽出する

1. 端の数牌と字牌の判定、および13牌種の集合・必要な展開をCoreへ導入する。
   `orphanKinds`と`kokushiKinds`の外延的一致を移行前後で示し、計算に使う実装を維持する。
2. 集合がちょうど13種、各字牌と各スートの1・9を含み、2〜8は含まないことを検証する。
   多重集合を共有する場合は各対象が1枚、非対象が0枚であることと総数を示す。
3. Shantenの国士計算・証明を共有定義へ切り替え、同義のlocal定義と不要な一致証明を削除する。
   国士の完成条件やシャンテン結果は変えない。

**完了条件:** Core側の定義と基本則、全34牌種の所属・13種・枚数の検査、Shantenの
国士の既存回帰と証明・ビルドが通ること。computableな利用箇所に`noncomputable`を
持ち込まないこと。移行後の旧宣言の不在をCIで検査すること。

### 2. 部品と牌カウントの基本則を整理する

1. `countsOfTiles_sum_eq_card`と`meldsTiles_card`を既存APIと照合し、Coreの共有基本則として
   必要なものを移す。Coreの既存`Pair.tiles_card`を直接使える箇所はwrapperを削る。
2. `tileCount`等は`Hand`に依存しない計数機能として独立させる意味がある場合にのみ移す。
   0・1・2・3・4枚の境界、同種4枚が1牌種として数えられることを確認する。
3. Shantenの証明と利用箇所を直接Core APIへ切り替え、同義定義と不要な橋渡しを削除する。

**完了条件:** リストと多重集合の違い、同一面子の反復、空集合、4枚カウントを含む
回帰検査と必要な定理の`sorry`不在検査が通ること。対象定義・wrapperの不在検査を追加すること。

### 3. 固定牌・不完全部品・特殊形を個別に判断する

1. 固定牌の形・占有・容量と、Shanten固有の有効手牌・入力契約を分離して比較する。
   順子・刻子・槓、固定牌だけの過剰占有、standingとの合計超過を含めて検討する。
2. `Taatsu`の対象範囲と完成選択、および待ち分類の部品を比較する。必要な共通概念があっても、
   検索用の一方向の完成選択をその定義と混同しない。
3. 特殊形の牌構成は、ルール・条件の一致を示せる範囲だけを独立に提案する。
   それぞれ**抽出／現状維持／別課題**を決め、理由・受入条件を記録してから着手する。

この段階は1・2とは独立して調査できるが、条件未確定の候補を完了扱いにしない。

### 4. 横断検証と資料更新

対象の移行ごとに、Coreの`lake build`、Shantenの`lake build`、
待ち分類の`lake build Mahjong MahjongTests`を実行する。W6は共有型移行の検証後に
解消済みであり、各側の仕様と回帰で検証を継続する。
Coreの基本則と影響を受けたconsumerの出口定理に`sorry`不在検査を設ける。
変更対象の振る舞いに応じて国士・七対子・固定槓・容量超過・入力エラーの既存例を確認する。
GoコードやGo契約を変更する場合は当該リポジトリで`go test ./...`と`go vet ./...`も実行する。

Coreと各consumerの用語集、既存の移行計画・状況資料に正本と未移行項目を反映する。
現行CIはCoreの`main`を参照するため、独立コミットの導入順をCore→consumerとし、
各リポジトリが参照する版の組み合わせを確認する。読みやすさの人手確認は
機械検証とは別の持ち越し項目として記録する。

## 全体の完了条件

- 各候補について抽出・現状維持・保留の理由があり、抽出した共有概念の正本がCoreにある。
- 移行済み概念のlocal定義・不要な変換・対応証明を除き、対象を明示した不在検査がある。
- 意味・前提・結果の回帰、関連Leanビルド、証明穴検査が通り、影響範囲に応じたGo検査が通る。
- 命名・APIの選択理由と、未確認の読みやすさ、人手確認、別課題が資料に残る。
