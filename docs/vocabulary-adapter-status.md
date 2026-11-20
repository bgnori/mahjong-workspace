# 共有ドメイン語彙とAdapterの現状

調査日: 2026-11-20

## 要約

3リポジトリには、牌・対子・面子に相当する語彙のローカル定義が
それぞれ残っています。ただし「共通定義もAdapterもない」状態ではありません。
`mahjong-domain-core`が共有Lean定義を持ち、待ち分類・シャンテン計算の両方に
既存型から共有型へのAdapterと対応証明があります。

したがって、Lean上で共有定義との意味の対応を作る作業はかなり進んでいます。
一方、各利用側のローカル型を廃止して共有型だけに統一する作業は未完了です。
Adapterは境界の対応を証明しますが、ローカル型宣言を置き換えるものではありません。

## リポジトリごとの定義とAdapter

| リポジトリ | ローカル／共有語彙 | Adapterの有無と範囲 |
|---|---|---|
| [mahjong-domain-core](../mahjong-domain-core/) | 共有定義の正本。`MahjongDomain.Tile`、`Pair`、`Meld`、`Kan.occupiedTiles`、`StandardDecomposition`、`StandardCompletion`を定義します。標準面子`Meld`は刻子または順子で、槓の占有枚数は`Kan.occupiedTiles`で別に表します。 | 他プロジェクトから共有される側なので、利用側型へのAdapterはありません。共通の意味は[Parts.lean](../mahjong-domain-core/MahjongDomain/Parts.lean)と[用語集](../mahjong-domain-core/docs/GLOSSARY.md)に集約されています。 |
| [mahjong-wait-classification](../mahjong-wait-classification/) | [Basic.lean](../mahjong-wait-classification/Mahjong/Basic.lean)に`Suit`、`Honor`、`Tile`、`PhysicalTile`等、[Pattern.lean](../mahjong-wait-classification/Mahjong/Pattern.lean)に`Toitsu`、`Shuntsu`、`MentsuCandidate`があります。`MentsuCandidate`は順子または刻子で、共有`Meld`と対応します。待ち分解・待ち核などはこのプロジェクト固有です。 | **あり**。[DomainAdapter.lean](../mahjong-wait-classification/Mahjong/DomainAdapter.lean)はスート・字牌・牌種・牌種カウントを往復変換し、対応証明を持ちます。物理牌は共有`PhysicalTileId`への変換と牌種・copy番号の保存を証明しますが、逆変換は定義されていません。[PartsAdapter.lean](../mahjong-wait-classification/Mahjong/PartsAdapter.lean)は`Toitsu`↔`Pair`、`MentsuCandidate`↔`Meld`、リストおよび標準分解を変換し、往復・牌数対応を証明します。 |
| [mahjong-shanten-calculation](../mahjong-shanten-calculation/) | [Core.lean](../mahjong-shanten-calculation/Shanten/Core.lean)に独自の`Suit`、`Tile`、`TileCounts`、`Meld`、牌 multiset 関数があり、`Meld`は共有定義と同じく刻子または順子です。対子は専用型でなく牌種から作る`pairTiles`で表します。`Hand`や固定面子管理は計算側のモデルです。 | **あり**。[DomainAdapter.lean](../mahjong-shanten-calculation/Shanten/DomainAdapter.lean)はスート・牌種・カウント・面子・面子列を変換し、往復変換と牌数対応を証明します。対子も牌種から共有`Pair`へ変換します。さらに`standardCompletion_iff_shantenParts`で共有完成仕様とShanten側仕様の同値性を示します。[Input37/DomainAdapter.lean](../mahjong-shanten-calculation/Shanten/Input37/DomainAdapter.lean)には37枠の正規化・容量・カウント集約を共有定義に結び付ける別Adapterもあります。 |

## 重複と意味差

- 牌種・スート・牌種カウント、対子、順子／刻子面子は複数リポジトリにローカル型・関数が残っています。Leanの共有定義をimportしていることと、ローカル定義が消えていることは別です。
- 待ち分類の`MentsuCandidate`は、現状のコンストラクタ範囲では共有`Meld`に全単射で対応します。ただし、`Toitsu`・`Shuntsu`等の分類側の公開型や列挙順まで共有型へ置き換えたわけではありません。
- シャンテン計算の`Meld`も共有`Meld`と同じ標準面子を表します。一方、固定面子を含む`Shanten.Capacity.FixedMeld`は標準面子または槓の占有を表す計算側の型であり、`Shanten.DomainAdapter`にはこの型の変換はありません。共有側では標準面子と槓占有を分けています。
- 待ち分類固有の待ち・和了構成部品・待ち核など、およびシャンテン計算固有の手牌、容量・探索仕様は共通面子語彙と同じ概念ではありません。ローカルにあることだけを理由に共通化対象とは判断できません。

## Lean以外の公開型について

確認したGoソースには`DomainAdapter`または`MahjongDomain`への接続がありません。
特にシャンテンのGo APIの[Meld](../mahjong-shanten-calculation/shanten.go)は
chi・pon・ankan・daiminkan・kakanと全物理牌を持つ契約型です。これはLean共有側の
隠れた標準面子`Meld`（順子／刻子）とは境界・意味が異なり、槓についても共有側は
`Kan.occupiedTiles`として占有を表します。したがって、Lean Adapterがあることを
Go APIの共有・変換まで完了した根拠にはできません。

## 残作業量の見立て

1. **Leanの共通意味を対応付けるだけなら、主要部分は実装済みです。** 両consumerに共有ドメインへのAdapterと証明があり、ゼロから共通型の変換・対応定理を作る必要はありません。
2. **ローカル宣言を削除して共有型へ統一するなら、移行作業は残っています。** Adapterを使う公開型・アルゴリズム・証明の依存を調整し、既存の名前や列挙順、分類結果の振る舞いを保つ必要があります。特に待ち分類側は既存型を保つ意図がAdapterの説明にも明記されています。
3. **Goも統一対象に含めるなら、別途スコープ設定が必要です。** 現状のLean AdapterはGoの入出力・固定面子契約を変換しません。Go側に必要な共通表現と境界を決める作業は、Leanの型置換とは別です。

従って、次の作業を見積もる際は「共有定義との対応付け」ではなく、
「どのローカルAPIを実際に共有型へ置換するか」と「Go APIも対象にするか」を
分けて数えるのが妥当です。
