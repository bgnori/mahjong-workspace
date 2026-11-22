# 共有ドメイン語彙への移行状況と対応計画

基準日: 2026-11-22

方針・詳細な意味対応: [共有ドメイン語彙とAdapterの現状](./vocabulary-adapter-status.md)
追加調査: [ShantenからCoreへの共有機能抽出計画](./shanten-core-extraction-plan-2026-11-22.md)

## 目的と適用方針

2026-11-22に更新された移行方針に基づき、完了済みの共通核の導入と、consumer側に残る
同義定義・Adapterの整理を分けて記録します。この計画はW0〜W7を再実施するものでは
ありません。実装の意味対応や個別概念の扱いは、上記の現状資料を正とします。

- Coreが共有ドメインの「what」を定義し、consumerは列挙・分類・探索などの「how」を
  実装します。同じwhatを表すlocal型と移行用Adapterは、直接利用への切替後に削除します。
- APIの改名に互換aliasは必須ではありません。意味・保証を照合してから切り替えます。
- Core `Pair`は同一牌種ちょうど2枚です。手牌中の3枚・4枚は`TileCounts`に保持し、
  そこから2枚を選びます。手牌中の4枚を固定`Kan`に変換しません。
- 候補の順序付き列挙や物理的な手牌などconsumer固有の使い方・状態はconsumerに残します。
  部品を構成する順序付き牌列はCoreを正本とし、分類の順序付き出力を維持します。
- Tenhou物理牌、Int37、Int34の表現・変換・容量規則はCoreを正本とし、Go実装も意味上
  の仕様に追随します。Goの言語に適した表現や固定済み`Meld`契約は維持します。
- `Completion`のconsumer横断統一・改名は本計画のブロッカーにせず、別課題として保留します。

## 対応状況

| 対象 | 状況 | 残っていること |
|---|---|---|
| `mahjong-domain-core` | **完了** | 共有`Shuntsu`／`MentsuCandidate`と`.shuntsu`／`.koutsu`、厳密な`Pair`、`TileCounts`からのPair分解を実装済み。Core build確認済み。 |
| `mahjong-shanten-calculation` Lean | **既存Core型への移行は完了** | 牌種・カウント・面子候補をCoreから直接利用。追加の共通機能抽出は[別計画](./shanten-core-extraction-plan-2026-11-22.md)で調査する。 |
| `mahjong-wait-classification` 面子部品 | **実装・機械検証済み、人手確認待ち** | Coreの部品型・牌種と順序付き展開を直接利用し、local型と`PartsAdapter.lean`を削除。回帰検査・CI不在検査あり。読解負荷の人手確認は未実施。 |
| `mahjong-wait-classification` 牌・物理牌表現 | **実装・機械検証済み、人手確認待ち** | Coreの牌種・index・`PhysicalTileId`を直接利用し、重複型と`DomainAdapter`を削除。列挙・ID・赤5境界と既存分類の回帰検査あり。 |
| Go実装 | **照合未完了** | 固定済み`Meld`契約は維持する。牌表現、Tenhou/Int37/Int34の順序、容量、赤5規則、および固定槓とstanding countsの境界をCoreと照合する。 |
| 不在検査・文書・読解負荷 | **未完了** | 完了した概念ごとのlocal宣言・移行用変換の不在検査、用語資料の同期、代表処理の読みやすさ比較を追加・記録する。 |

## 実施計画

順序は **Core（完了）→ wait-classification → adapter整理・完了検査** とします。
Shantenの既存Core型へのLean移行は完了済みです。追加の共有機能抽出は別計画で進めます。
Go照合はCoreの表現規則に対する確認なので、wait-classification
の移行と並行して実施できます。各段階は意味・振る舞いの確認を通過してから完了扱いにします。

### 1. wait-classificationの面子部品をCore型へ移す（人手確認待ち）

**対象:** `Toitsu`、`Shuntsu`、`MentsuCandidate`、`PartsAdapter.lean`と直接の利用箇所。

1. Coreの`Pair`、`Shuntsu`、`MentsuCandidate`を使うよう利用箇所と通常形接続の証明を切り替える。
2. Coreの順序付き牌列を正本とし、`Multiset`展開をそこから導出する。
   牌種Adapter経由の多重度の一致を証明し、列順は別の保証として扱う。
3. Core型を直接利用できることを確認してからlocal型、`PartsAdapter`の型変換・往復証明を削除する。
   分類固有の候補列挙は残す。
4. 牌列順、候補列挙順、分類ID・結果、重複数について既存回帰例を確認し、不足する境界例を追加する。

**完了条件:** 対象型の重複と不要なParts adapterがなく、Multisetとの対応証明・順序・結果の回帰検査が
あること。残す例外は対象・理由・解消条件を記録すること。`lake build Mahjong MahjongTests`が成功し、
対象宣言の不在検査が追加されていること。代表処理で追う型・変換・証明の数と変換段数を移行前後で
比較し、式や証明が複雑化していないかも確認すること。

**実施結果:** 3型をCoreから直接利用し、`PartsAdapter.lean`を削除した。当初は部品ごとの
順序付き展開と対応証明が分類側に残っていたが、Coreの`orderedTiles`を正本にし、
`tiles`をそこから導出した。分類側は共通の計数補題を利用する。当初残っていた牌種Adapterは段階2で削除した。
候補の列挙順、端の順子、刻子、
同一面子の重複と分解順、待ち・分類コードの順序と重複数について回帰例を確認した。
CIに旧部品型・変換宣言と`PartsAdapter.lean`の不在検査を追加した。
分類側の`lake build Mahjong MahjongTests`、`go test ./mahjong`、Shantenとの固定文脈連携
`w6`の`lake build`が隔離環境で成功した。展開対応と通常完成への接続は`sorry`不在も検査する。

**読解負荷の比較（最初の部品型移行時点）:** 対象を`WinningPartitionSpec.toDomainStandardCompletion`から
Pairと面子候補の共有カウントに至る経路に固定する。型はlocalとCoreのPair・面子候補の
計4定義からCoreの2定義となった。部品変換は`toDomainDecomposition`、
`toDomainPair`、`toDomainMentsuCandidates`、`toDomainMentsuCandidate`の4宣言から0となり、
面子候補への最長変換経路は3段から0段となった。牌種の変換は両時点で残る。
同経路の部品カウント／展開の対応定理は5から6になった（順子単体の展開対応を明示したため）。
対子の牌展開を探す場合の候補宣言は2から2のままである（移行前はlocalの`Toitsu.tiles`と
Coreの`Pair.tiles`、移行後は分類側の`ClassificationPair.tiles`とCoreの`Pair.tiles`）。
その後、順序付き列はCoreを正本にし、分類側の列はその写像となった。部品ごとの
`orderedTiles_toDomain`対応定理は共通の計数補題に置き換えた。
これらは代理指標であり、複雑さや読みやすさの人手確認は未実施のため、本段階を最終完了にはしない。

### 2. wait-classificationの牌・物理牌表現をCoreへ移す

**対象:** `Suit`、`Honor`、`Tile`、牌種index、`PhysicalTile`と`DomainAdapter.lean`。

1. `Tile.numbered`とCore `Tile.suited`、スート名、牌種indexについて、値の意味・順序・利用箇所を照合する。
   名前候補に未決定事項がある場合は、現状資料で定めた代表コードの読みやすさ評価を行い、結果と判断理由を残す。
2. Coreの牌種とindexを直接利用し、分類側で必要なソート・列挙方法はconsumer側に残す。
3. `PhysicalTile`からCore `PhysicalTileId`への移行では、牌種・copy・Tenhou順IDの対応を証明し、
   物理牌の列挙順やHandの不変条件を確認する。
4. 各表現の利用が切り替わった範囲から不要な変換とlocal定義を削除する。
   `DomainAdapter`全体は未移行の対応が残る間は維持し、一括削除しない。

**スートの実施結果:** `Suit`はCoreを直接使い、旧型と双方向変換・往復証明を削除した。
分類上のスート順はCoreの`Suit.all`を使い、分類キーは同じ順から得る。代表例では旧
`WinningComponent.shuntsu .Pinzu start`を`.pin`へ、`.numbered .Manzu rank`を`.man`へ
変更した。`Manzu`等は日本語の名称が明示的だが、Coreの`man/pin/sou`はmpszの色表記と
対応し、既存Core APIを通じて分類とShantenの同じ概念を一貫して読めるため採用した。
人手による読みやすさ確認は引き続き未実施。

**牌種・物理牌の実施結果:** Core `Tile`、`Honor`、`TileFormat`、`PhysicalTileId`を直接使用し、
旧ローカル型と`DomainAdapter.lean`、Shanten連携の牌変換・往復証明を削除した。
`Hand`の埋め込みは位置ごとに物理IDを保持し、同じIDの重複禁止と位置順を維持する。
旧Adapterは`index * 4 + copy`の牌種・copy保存を証明していた。移行後は任意のIDを
その牌種indexと余りで再構成できること、34牌種の列挙順、各色の赤5と通常5の境界を
検査する。`deck`は有限集合であり、その列挙順を公開契約として扱わない。
既存の待ち・分類コード・重複・表示例とCI不在検査も維持する。

**名前と読解負荷:** 旧`WinningComponent.pair (.numbered .man 4)`は
`WinningComponent.pair (.suited .man 4)`、旧`.honor .East`は
`.honor Honor.east`となる。`numbered`は数牌であることを強調する一方、`suited`は
字牌と対比して「スートを持つ牌」という共通構造を示すため、Coreのwhatとして採用した。
字牌は`Fin 7`のまま名前付き定数を提供する。完成証明は牌種変換と往復を追わず、
Coreの順序付き展開と計数補題を直接使う。これらの比較は人手による読みやすさ確認を
代替せず、確認は未実施。

**完了条件:** 各移行対象の値・index・物理牌IDの対応根拠があり、重複定義と不要な変換が削除されていること。
列挙順・物理牌制約など既存挙動の回帰検査と宣言の不在検査を追加し、Lean build・テストが成功すること。
未決定の識別子は決定理由とともに現状資料へ反映すること。

### 3. Go契約をCoreの表現仕様と照合する（並行可）

**対象:** Goの牌表現、Tenhou/Int37/Int34変換・容量・赤5規則、standing countsと固定槓。

1. Coreの規則とGo実装の対応を項目別に照合する。Goの`Meld`は固定済み入力契約として維持し、
   Core `MentsuCandidate`とは統合しない。
2. 差分がある場合は既存契約を確認し、意図した挙動を保つ境界テストを追加してから修正する。
3. 対応する数値テストがなければ、Goのテスト成功はビルド確認に留まることを記録する。

**完了条件:** 表現・変換・容量・赤5規則と固定槓の境界がCore仕様と一致すること。
差分があった場合はテストで確認され、`go test ./...`と`go vet ./...`が成功すること。

### 4. 残存Adapter・重複を片付け、完了状態を記録する

**前提:** 各対象概念がconsumerから直接Core利用され、意味対応のためだけのAdapterが不要であること。

1. 意味変換が不要になったAdapter、local型、wrapper、往復証明を削除する。
   consumer固有の状態・操作、および移行中の別表現に必要なAdapterは理由を添えて残す。
2. 対象概念ごとに正本と禁止するlocal宣言・変換を列挙し、その概念の移行完了後にCIの不在検査を追加する。
   未移行の概念を検査対象の完了扱いにしない。
3. glossary、API説明、移行状況を実装と一致させる。`Completion`の意味・名前の見直しは別課題のままとする。
4. Lean build、wait-classificationのLeanテスト、および該当するGo検査を実行し、読解負荷の比較結果を記録する。

**全体完了条件:** 同じwhatを表すlocal型が移行対象に残らず、利用中の変換・証明には未移行または
consumer固有の理由があり、対応する不在検査・回帰検査が通ること。読み手が追う境界が減り、
式や証明の複雑さを悪化させていないことを人が確認すること。

## 対象外・保留

- `Completion`をconsumer横断で統合・改名すること。意味、入力条件、証拠形式が異なるため別課題とします。
- wait-classification固有の待ち分解、`WaitCore`、物理的`Hand`、候補の順序付き列挙のCore移管。
- Shanten固有の`Hand`、現在の`Taatsu`、容量・探索方針のそのままの共有化。
  `Taatsu`や固定牌のうち共有可能な概念があるかは[別計画](./shanten-core-extraction-plan-2026-11-22.md)で再検討する。
- Goの固定済み入力契約`Meld`をLeanの標準形候補へ統合すること。
- 未決定のAPI名を、代表コードの評価・意味確認なしに一括改名すること。
