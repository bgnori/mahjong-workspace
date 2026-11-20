# 共有ドメイン語彙とAdapterの現状

調査日: 2026-11-20

## 要約

3リポジトリには、牌・対子・面子に相当する語彙のローカル定義が
それぞれ残っています。ただし「共通定義もAdapterもない」状態ではありません。
`mahjong-domain-core`が共有Lean定義を持ち、待ち分類・シャンテン計算の両方に
既存型から共有型へのAdapterと対応証明があります。一方、共有型名の`Meld`は
副露状態を表さない構造型であり、固定面子を指す`Meld`との混同が実際に起きています。

したがって、Lean上で共有定義との意味の対応を作る作業はかなり進んでいます。
一方、各利用側のローカル型を廃止して共有型だけに統一する作業は未完了です。
Adapterは境界の対応を証明しますが、ローカル型宣言を置き換えるものではありません。

## 共有語彙名の再評価

共有`Meld`が表すのは、牌種構成としての刻子または順子です。コンストラクタに
副露・暗槓・門前の区別はなく、槓の4枚占有も`Kan.occupiedTiles`として別に
表現されています。したがって、共有`Meld`は「副露された組」ではありませんが、
型名だけではその違いが分かりません。

これは用語上の潜在的な問題に留まりません。シャンテン側の
[用語集](../mahjong-shanten-calculation/docs/GLOSSARY.md)では、Go契約の固定面子を
副露・暗槓などの入力済み面子、Leanの`Meld`を探索中の完成面子として別項目で
説明しています。Goの`Meld`とLeanの`Meld`で意味が異なることも同じ用語集で注意
されています。共有コア自身の[用語集](../mahjong-domain-core/docs/GLOSSARY.md)も
現在の項目名を`Standard meld`としていますが、識別子は修飾のない`Meld`です。
文書の修飾だけでは、型名に接する利用者の誤読を防ぎきれません。

**推奨:** 共有型の名前は`MentsuShape`のように、完成形の構造を表すと分かる語へ
改めるのがよさそうです。`MentsuShape`なら副露状態を含意せず、共有型が持つ
「順子または刻子の牌構成」という範囲を示せます。`StandardMeld`は現行Glossaryの
表現を保てますが、`Meld`自体が副露済みの組と読まれる問題は残ります。
`ConcealedMeld`は現行の探索スコープには合っても、型自体が門前・副露状態を
保持していないため、共有型の本質的な意味を表す名前としては避けるべきです。

この名前変更は今回の調査では実施していません。`Meld`、`MeldList`、
`StandardDecomposition.melds`等の共有APIと、両consumerのAdapter・証明名へ波及
します。意味対応の証明は既にあるのでゼロからのモデル設計ではありませんが、
公開APIの互換性を保つ別名を設けるかも含めて、改名方針を決める必要があります。
副露状態そのものを共有型に追加するのは別の要件であり、現在の`MentsuShape`候補に
その状態を混ぜる必要はありません。Goの入力契約やシャンテン側の固定面子型など、入力時点で固定済みの
組を扱う境界型とは分けます。

## リポジトリごとの定義とAdapter

| リポジトリ | ローカル／共有語彙 | Adapterの有無と範囲 |
|---|---|---|
| [mahjong-domain-core](../mahjong-domain-core/) | 共有定義の正本。`MahjongDomain.Tile`、`Pair`、`Meld`、`Kan.occupiedTiles`、`StandardDecomposition`、`StandardCompletion`を定義します。`Meld`は順子または刻子の構造のみを表し、副露状態は持ちません。槓の占有枚数は`Kan.occupiedTiles`で別に表します。 | 他プロジェクトから共有される側なので、利用側型へのAdapterはありません。共通の意味は[Parts.lean](../mahjong-domain-core/MahjongDomain/Parts.lean)と[用語集](../mahjong-domain-core/docs/GLOSSARY.md)に集約されています。 |
| [mahjong-wait-classification](../mahjong-wait-classification/) | [Basic.lean](../mahjong-wait-classification/Mahjong/Basic.lean)に`Suit`、`Honor`、`Tile`、`PhysicalTile`等、[Pattern.lean](../mahjong-wait-classification/Mahjong/Pattern.lean)に`Toitsu`、`Shuntsu`、`MentsuCandidate`があります。`MentsuCandidate`は順子または刻子で、共有`Meld`と対応します。待ち分解・待ち核などはこのプロジェクト固有です。 | **あり**。[DomainAdapter.lean](../mahjong-wait-classification/Mahjong/DomainAdapter.lean)はスート・字牌・牌種・牌種カウントを往復変換し、対応証明を持ちます。物理牌は共有`PhysicalTileId`への変換と牌種・copy番号の保存を証明しますが、逆変換は定義されていません。[PartsAdapter.lean](../mahjong-wait-classification/Mahjong/PartsAdapter.lean)は`Toitsu`↔`Pair`、`MentsuCandidate`↔`Meld`、リストおよび標準分解を変換し、往復・牌数対応を証明します。 |
| [mahjong-shanten-calculation](../mahjong-shanten-calculation/) | [Core.lean](../mahjong-shanten-calculation/Shanten/Core.lean)に独自の`Suit`、`Tile`、`TileCounts`、`Meld`、牌 multiset 関数があり、`Meld`は共有定義と同じく刻子または順子です。対子は専用型でなく牌種から作る`pairTiles`で表します。`Hand`や固定面子管理は計算側のモデルです。 | **あり**。[DomainAdapter.lean](../mahjong-shanten-calculation/Shanten/DomainAdapter.lean)はスート・牌種・カウント・面子・面子列を変換し、往復変換と牌数対応を証明します。対子も牌種から共有`Pair`へ変換します。さらに`standardCompletion_iff_shantenParts`で共有完成仕様とShanten側仕様の同値性を示します。[Input37/DomainAdapter.lean](../mahjong-shanten-calculation/Shanten/Input37/DomainAdapter.lean)には37枠の正規化・容量・カウント集約を共有定義に結び付ける別Adapterもあります。 |

## 重複と意味差

- 牌種・スート・牌種カウント、対子、順子／刻子面子は複数リポジトリにローカル型・関数が残っています。Leanの共有定義をimportしていることと、ローカル定義が消えていることは別です。
- 待ち分類の`MentsuCandidate`は、現状のコンストラクタ範囲では共有`Meld`に全単射で対応します。ただし、`Toitsu`・`Shuntsu`等の分類側の公開型や列挙順まで共有型へ置き換えたわけではありません。
- シャンテン計算の`Meld`も共有`Meld`と同じ順子／刻子の形を表します。一方、固定面子を含む`Shanten.Capacity.FixedMeld`は標準面子または槓の占有を表す計算側の型であり、`Shanten.DomainAdapter`にはこの型の変換はありません。共有側では標準面子と槓占有を分けています。
- 「`Meld`は副露状態ではなく形を表す」という意味差は実装上明確ですが、識別子は区別しにくいままです。共有名を改めるなら、両consumerに既にある往復Adapterを改名の境界として使えます。
- 待ち分類固有の待ち・和了構成部品・待ち核など、およびシャンテン計算固有の手牌、容量・探索仕様は共通面子語彙と同じ概念ではありません。ローカルにあることだけを理由に共通化対象とは判断できません。

## ほかの同義語・別名の候補

以下は3リポジトリの宣言とAdapterを比較し、同じ概念または同じ写像を別の名前で
表している候補です。推奨は名前の整理案であり、この調査では識別子を変更していません。

| 対応する名前 | 一致度・根拠 | 改名を検討する場合 |
|---|---|---|
| Core `Pair` ↔ 待ち分類 `Toitsu` | **高。** いずれも同一牌種2枚の組です。`PartsAdapter`に双方向変換と往復定理があります。`Toitsu`は分類モデルの型、`Pair`は共有分解の部品名という語感・用途の違いはありますが、表している牌構成は一致します。 | 共有語彙`Pair`を標準名として、分類側で既存API互換性を保つ間はAdapterを別名境界として残すのが低リスクです。分類側の公開型まで統一するなら、`Toitsu`とその`.toitsu` constructorをまとめて移行します。 |
| Core `Meld.sequence` ↔ 待ち分類 `Shuntsu` / `MentsuCandidate.shuntsu`、および `Meld.triplet` ↔ `MentsuCandidate.koutsu` | **高。** 同じ数牌順子／同一牌種の刻子です。`PartsAdapter.toDomainMeld`はそれぞれを`.sequence`／`.triplet`へ写し、両方向の往復を証明します。シャンテン側は最初から`.sequence`／`.triplet`です。 | 共有型名を`MentsuShape`にする場合も、内部constructorは`.sequence`／`.triplet`が意味を明確に保ちます。分類側の`.shuntsu`／`.koutsu`は既存名として当面維持し、必要ならAPI移行時に一括改名します。 |
| Core/Shanten `Tile.suited` ↔ 待ち分類 `Tile.numbered` | **高。** どちらもスートとランクで表す27種類の数牌で、待ち分類Adapterが直接対応させています。対する字牌constructorは両方`.honor`です。 | Core/Shanten側の`.suited`を共通名にするのが自然です（両consumerの共有モデルですでに一致）。待ち分類側の`.numbered`は旧APIとして残すか、公開API改名時に移行します。 |
| Core `Suit.man/pin/sou` ↔ 待ち分類 `Suit.Manzu/Pinzu/Souzu` | **高。** 3つのスートが要素ごとに双方向対応し、Adapterの往復定理があります。違いは略記と日本語ローマ字表記です。 | 意味改善は小さいため優先度は低めです。共通APIに寄せる場合は`man/pin/sou`を基準とできますが、表記を明示する既存名を互換性のため維持する案も妥当です。 |
| Core `Int37Index.tile` ↔ Shanten `Input37.normalizeTile`、および Core `Tile.int37Index` ↔ Shanten `Input37.normalIndex` | **高（同じ写像）。** 前者は37スロットから正規化牌種へ、後者は牌種から赤5を分けない通常の37スロットへ写します。後者は共有写像との一致定理があり、Shanten側の`normalizeTile`もCoreの写像を呼び出す薄いwrapperです。 | 重複アルゴリズムはありません。Coreのnamespace付き名前は`.tile`、Shantenの公開語は`normalizeTile`／`normalIndex`で、利用側の意図が読み取りやすい利点があります。改名は不要で、用語集に対応名を記録するだけで十分です。 |
| Core `aggregateInt37` ↔ Shanten `Input37.normalizeCounts` | **高（同じ集約）。** 同じ37枠の符号付きカウントを、赤5を通常5へまとめた牌種別カウントへ集約します。Shanten wrapperは共有関数を呼び、加法・容量等の性質も共有定理へ接続しています。 | Core名`aggregateInt37`を数理操作の標準名にできますが、Shantenの`normalizeCounts`は入力処理の語彙として分かりやすい名前です。実装重複がないため改名優先度は低く、必要ならShanten公開APIを変更する段階で別名化を検討します。 |
| Core `Int37Counts` ↔ Shanten Lean `Input37.Counts37` | **完全一致（型alias）。** `Input37.Counts37`は`MahjongDomain.Int37Counts`の`abbrev`であり、独立したカウント表現ではありません。Goの`Counts37`は固定長配列`[37]int`なので、同じ要素数でもLean aliasとは型・言語境界が異なります。 | Lean内のAPI名を揃えるなら`Int37Counts`を直接使うか、互換性用aliasとして`Counts37`を残します。Goの公開型まで同一視する改名は避け、言語・表現の違いを明記します。 |
| Core `Tile.index` ↔ 待ち分類 `Tile.orderKey` | **高（値の対応）、ただし型・用途は異なる。** 共有の有限添字`Fin 34`と分類側のソート用`Nat`について、`DomainAdapter.tileIndex_val`が値の一致を証明します。 | 同じ宣言の重複ではなく、共有側は範囲証拠付き添字、分類側は順序キーです。ソート用途を明示する`orderKey`には意味があるため、無理に同名化する必要はありません。共通比較の箇所では変換を明示します。 |
| Core `PhysicalTileId : Fin 136` ↔ 待ち分類 `PhysicalTile := Tile × Fin 4` | **同じ牌種×コピーの有限集合を表す別表現。** 分類側からCoreへの変換と牌種・copy保存定理はありますが、逆変換の定義・往復定理はありません。CoreはTenhou順の安定ID、分類側は牌種とコピー番号の組を選んでいます。赤5をcopy 0とする規約はCore側で明示されていますが、分類側の型定義自体は赤5規約を表していません。 | 単純な名前置換ではなく表現選択です。Coreの安定IDを標準にするなら逆変換・全単射証明と利用箇所の移行が必要です。赤5規約まで共通化するかは別途確認が必要です。両表現を併存するなら、`PhysicalTile`を値、`PhysicalTileId`を外部IDとして呼び分ける現状には理由があります。 |
| Core `StandardCompletion` ↔ 待ち分類 `WinningPartitionSpec` / `IsStandardAgari` ↔ Shanten `Complete .mentsuHand` | **近縁だが同一ではない。** いずれも通常形の雀頭＋面子分解を述べ、既存の変換・同値定理があります。しかし、Coreは牌種カウントと面子数、待ち分類は牌リストと分割証人、Shantenは4枚制限・固定面子文脈を含みます。 | 共通の数学的核として相互変換を維持するのは有益ですが、公開述語名を一つに揃えるのは不適切です。各述語の条件・証拠形式を明記し、共通完成仕様との対応定理名を統一する程度が妥当です。 |

### 改名の優先順位

1. **高:** `Meld`→`MentsuShape`（前節）、および順子／刻子constructor名を共有API内で明確にする。既存Adapterがあるため意味モデルの作り直しは不要ですが、共有APIと両consumerの識別子・証明名をまとめて移行します。
2. **中:** `Toitsu`↔`Pair`、`Shuntsu`↔`sequence`、`Koutsu`↔`triplet`、`.numbered`↔`.suited`。意味対応は既に証明済みです。公開名まで統一する場合の負担は主にLeanソースの参照更新・互換性判断であり、対応関係の再証明は小さくできます。
3. **低:** `normalizeTile` / `normalIndex` / `normalizeCounts`など共有写像の利用側wrapper名、および`Suit` constructor表記。wrapperはCoreに委譲済みで、名前を揃えても定義重複はさらに減りません。
4. **現時点で改名非推奨:** `PhysicalTile`と`PhysicalTileId`は同じ有限対象を別の有用な表現で持ちます。`Tile.index`と`Tile.orderKey`も、値は対応していても有界添字とソートキーという利用上の差があります。また、完成仕様の述語群は条件範囲が異なるため、一つの名前に統合しません。

この比較から、**重複実装の整理**と**同じ意味の語彙名の統一**は分けて扱うべきです。
Int37の写像のように実装が既に共有されているものは、名前の違いを解消しても作業量・
正しさはあまり変わりません。一方、公開型名やconstructor名を統一する場合は、既存利用者
への互換性方針が作業量を左右します。

## Lean以外の公開型について

確認したGoソースには`DomainAdapter`または`MahjongDomain`への接続がありません。
特にシャンテンのGo APIの[Meld](../mahjong-shanten-calculation/shanten.go)は
chi・pon・ankan・daiminkan・kakanと全物理牌を持つ契約型です。これはLean共有側の
通常形面子`Meld`（順子／刻子）とは境界・意味が異なり、槓についても共有側は
`Kan.occupiedTiles`として占有を表します。したがって、Lean Adapterがあることを
Go APIの共有・変換まで完了した根拠にはできません。

## 残作業量の見立て

1. **Leanの共通意味を対応付けるだけなら、主要部分は実装済みです。** 両consumerに共有ドメインへのAdapterと証明があり、ゼロから共通型の変換・対応定理を作る必要はありません。
2. **ローカル宣言を削除して共有型へ統一するなら、移行作業は残っています。** Adapterを使う公開型・アルゴリズム・証明の依存を調整し、既存の名前や列挙順、分類結果の振る舞いを保つ必要があります。特に待ち分類側は既存型を保つ意図がAdapterの説明にも明記されています。
3. **Goも統一対象に含めるなら、別途スコープ設定が必要です。** 現状のLean AdapterはGoの入出力・固定面子契約を変換しません。Go側に必要な共通表現と境界を決める作業は、Leanの型置換とは別です。

従って、次の作業を見積もる際は「共有定義との対応付け」ではなく、
「どのローカルAPIを実際に共有型へ置換するか」と「Go APIも対象にするか」を
分けて数えるのが妥当です。
