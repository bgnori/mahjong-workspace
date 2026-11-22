# 共有ドメイン語彙とAdapterの現状

調査日: 2026-11-20
方針更新日: 2026-11-22

更新前の記録は[履歴資料](./vocabulary-adapter-status-2026-11-20-archive.md)に保存しています。

## 要約

`mahjong-domain-core`には共有Lean定義があり、シャンテン計算は牌種・カウント・
面子候補を直接利用します。待ち分類にはローカル定義と共有仕様へのAdapterが残ります。
Adapterは段階移行のための境界であり、移行可能な重複定義をCoreの直接利用へ
収束させる方針です。以下の比較・改名検討には調査時点の記述も含みます。

Coreが「何であるか（what）」を定義し、consumerがそれを用いた探索・分類・評価など
「どう使うか（how）」を定義します。公開API名の改名に互換性エイリアスは要らない前提で
進められますが、同じ語を不用意に一対一対応させず、概念の意味を確認してから統合します。

Tenhou物理牌、Int37、Int34の表現・変換・容量規則はCoreが責任を持つ対象です。
consumerはCoreの表現上で必要な処理を定義し、Go実装もそのCore仕様に追随します。

移行の目的は、仕様のずれの防止、証明境界の単純化、保守箇所の削減に加え、
Leanコードを読む負荷と似た定義を読み比べる機会を減らすことです。使い方の違いは
主にconsumer側に現れます。順序付き列挙などの処理をconsumerに残す必要があっても、
同じ概念の型まで重複させる理由にはなりません。

## 型と使い方の分離・読みやすさの検証

| 共通概念 | 型の正本 | 待ち分類に残す使い方 |
|---|---|---|
| 対子 | Core `Pair` | 順序付き牌列への展開など |
| 順子 | Core `Shuntsu` | 順序付き牌列への展開など |
| 面子候補 | Core `MentsuCandidate` | 候補の列挙順、順序付き展開など |

上表は移行先の方針であり、現在は分類側に重複型とAdapterが残っています。
Coreの`tiles`が`Multiset`を返すことを理由に分類側の型を複製せず、Core型を
入力とする分類側の`List Tile`展開・列挙を検討します。分類固有の状態や操作は
それ自体を共有化せず、型を直接利用できない障害があれば具体的に記録して解消します。

### 機械的に確認する範囲

- 対象概念ごとに、正本と移行後に禁止するローカルの型・変換宣言を明示し、
  その対象が移行完了した段階でCIに不在検査を追加します。未移行分は完了扱いせず、
  残す例外には対象・理由・解消条件を記録します。この検査は指定した宣言を検出する
  もので、別名の意味的な重複まで自動判定するものではありません。
  部品型の対象は分類側の`Toitsu`、`Shuntsu`、`MentsuCandidate`と対応する
  `PartsAdapter`の型変換・往復証明です。分類固有の順序付き操作は対象に含めません。
- consumerの順序付き展開について、`Multiset.ofList`で順序を忘れた結果がCoreの
  展開と等しいことを証明します。これは牌種と多重度の一致を保証しますが、列順は
  保証しません。別途、分類の牌列順、候補列挙順、分類ID・結果と重複数について、
  既存の回帰例を確認し、不足する境界例を追加します。牌種が未移行の段階では、
  既存Adapterによる牌種の写像を含めて比較し、直接利用後は不要な写像を取り除きます。
- Lean buildと既存テストは型・証明・振る舞いの検証に使い、読みやすさの合格判定
  と混同しません。検査や証明を追加する作業自体も移行の完了条件です。

### 読解負荷と命名の評価

移行前後の同じ代表処理について、参照する型定義・変換・往復定理の数、共有仕様に
至る型変換の段数、同じ操作を探すときの候補宣言数を比較します。対象箇所と数え方を
固定して結果を記録し、読み手が追う境界が減ったかを確認します。これらは
読解負荷の代理指標であり、短さや数だけのスコアをCIの合否条件にはしません。
定義をまとめた結果、式や証明がかえって複雑にならないかも人が確認します。

`Tile.suited`／`numbered`、`Suit.man/pin/sou`／`Manzu/Pinzu/Souzu`など未決定の
名前は、全面移行・改名する前に、順子の牌展開や字牌の分岐など同じ短い代表コードで
候補を比較します。名前以外の構造は揃え、候補の由来や推奨を伏せて読み手に概念・
出力・区別しないものを説明してもらい、正誤と確認した箇所を記録します。所要時間は
補助情報とし、少人数の結果は絶対評価としません。Coreの字牌は現在`Fin 7`なので、
名前だけでなく値の意味を読めるかも確認します。候補と結果、判断理由を残し、
決まるまでは未決定として扱います。Coreの意味を明確にしつつconsumerで読めることを
重視し、利用箇所の数だけで決めません。

## 共有語彙名の再評価

旧共有`Meld`が表していたのは、牌種構成としての刻子または順子です。コンストラクタに
副露・暗槓・門前の区別はなく、槓の4枚占有も`Kan.occupiedTiles`として別に
表現されていました。したがって、旧共有`Meld`は「副露された組」ではありませんが、
型名だけではその違いが分かりませんでした。

これは用語上の潜在的な問題に留まりません。当時のシャンテン側の
[用語集](../mahjong-shanten-calculation/docs/GLOSSARY.md)では、Go契約の固定面子を
副露・暗槓などの入力済み面子、Leanの`Meld`を探索中の完成面子として別項目で
説明していました。Goの`Meld`とLeanの`Meld`で意味が異なることも注意されていました。
当時の共有コア自身の[用語集](../mahjong-domain-core/docs/GLOSSARY.md)も
項目名を`Standard meld`としていましたが、識別子は修飾のない`Meld`でした。
文書の修飾だけでは、型名に接する利用者の誤読を防ぎきれません。

**決定:** Coreの共有型名はwait-classificationの`MentsuCandidate`を採用し、
constructor語彙も`.shuntsu`／`.koutsu`を採用します。順子は共有`Shuntsu`型
（`.shuntsu (suit : Suit) (start : Fin 7)`）、刻子は牌種で表します。
`MentsuCandidate.shuntsu`は`Shuntsu`を受け取り、`.koutsu`は`Tile`を受け取るAPIと
します。これは副露状態を含まない標準形の完成面子候補で、Goの固定済み入力契約`Meld`とは
別概念として維持します。

**決定:** Coreの`Pair`は厳密に同一牌種2枚を表す型として維持します。2枚以上ある牌種
から対子を取り出す元は、新しい「2〜4枚のPair」型ではなく、既存の`TileCounts`
（牌種ごとの枚数）です。ある牌種のカウントが2以上なら、その2枚を`Pair`として
分解・選択できます。余剰の同種牌は残りのカウントに残し、`Pair`の意味を広げません。

同一牌種4枚が手の内にある状態は、あくまで手牌の`TileCounts`が4である状態です。
`Kan.occupiedTiles`が表す4枚は固定されたカンであり、枚数が同じでも手の内の4枚とは
異なるドメイン概念です。両者を同じ型や変換として扱いません。

Shantenの`pairCount`は2枚以上ある牌種の種類数を数える量で、Pairオブジェクトや牌を
消費する抽出操作ではありません。Shantenの牌カウント表現・固定槓と、Coreの`Pair`・
`Kan`は、移行時にもそれぞれの意味を保ちます。Coreの`TileCounts`自体は現在任意の
自然数カウントを許すため、物理牌上限4は有効な手牌・表現の妥当性条件として扱い、
`Pair`の型には持ち込みません。

公開APIの改名は許容され、歴史的互換性のための別名を維持する必要はありません。
実装移行では意味対応を確認するAdapterと証明を活用し、consumerがCore型を直接使う
ようになった範囲から、重複定義と移行用Adapterを削除します。

## リポジトリごとの定義とAdapter

| リポジトリ | ローカル／共有語彙 | Adapterの有無と範囲 |
|---|---|---|
| [mahjong-domain-core](../mahjong-domain-core/) | 共有定義の正本。`Tile`、厳密に2枚を表す`Pair`、`Shuntsu`／`MentsuCandidate`（`.shuntsu`／`.koutsu`）、`Kan.occupiedTiles`、`StandardDecomposition`、`StandardCompletion`を定義します。`Pair.counts_eq_pair_add_remaining`で、2枚以上ある牌種からPairを選んだ残余カウントとの再構成を保証します。固定カンは手牌カウントとは別概念です。 | consumer向けAdapterはありません。共通の意味は[Parts.lean](../mahjong-domain-core/MahjongDomain/Parts.lean)と[用語集](../mahjong-domain-core/docs/GLOSSARY.md)に集約されています。`StandardCompletion`の意味・名前の見直しは保留です。 |
| [mahjong-wait-classification](../mahjong-wait-classification/) | [Basic.lean](../mahjong-wait-classification/Mahjong/Basic.lean)に`Suit`、`Honor`、`Tile`、独自の`PhysicalTile`等、[Pattern.lean](../mahjong-wait-classification/Mahjong/Pattern.lean)に意図を持って命名された`Toitsu`、`Shuntsu`、`MentsuCandidate`があります。待ち分解・待ち核などはこのプロジェクト固有で、共有しない分類ロジックです。用語集は[こちら](../mahjong-wait-classification/docs/GLOSSARY.md)です。 | **あり（移行用）。** 現在の`DomainAdapter.lean`／`PartsAdapter.lean`で対応を証明しています。移行時はCore定義の利用へ切り替え、同じ概念のlocal定義とAdapterを最終的に削除します。待ち分類で吟味済みの語は、共有名を決める際の有力な指針です。 |
| [mahjong-shanten-calculation](../mahjong-shanten-calculation/) | Coreの`Suit`、`Tile`、`TileCounts`、`MentsuCandidate`を直接使います。`Hand`はカウントと固定面子数だけを持つ抽象状態です。`Capacity.FixedMeld`は標準形または槓を固定文脈として持ちます。用語集は[こちら](../mahjong-shanten-calculation/docs/GLOSSARY.md)です。 | 型変換Adapterと`Input37`の重複wrapperは削除済み。`Int37Counts`、`Int37Index.tile`、`Int37Index.capacity`、`aggregateInt37`を直接使います。通常完成の対応定理は`Specification.lean`にあります。 |

## 重複と意味差

- 待ち分類には牌種・スート・牌表現・面子形の重複定義が残っています。Adapterは意味対応の証拠として有用ですが、移行可能な範囲ではCore型へ直接移行し、local宣言と移行用Adapterを削除します。
- 既存`Toitsu`↔`Pair` adapterの往復定理は、両者が「ちょうど2枚」を表すため成立します。改定後もPairの意味は広げず、同種牌が3枚・4枚あるときは`TileCounts`から2枚を選び、残りを別に保ちます。
- Coreでは共有`Meld`を`MentsuCandidate`へ改名し、共有`Shuntsu`と`.shuntsu`／`.koutsu`語彙を実装しました。ShantenもこのAPIを直接使います。関係述語など、構造型とは異なる概念は必要に応じて別に定義します。
- シャンテンの`Hand`は共通の物理牌手ではなくカウント状態です。待ち分類の物理的`Hand`はconsumer固有で共有化しにくく、Coreに移す対象は`Hand`そのものではなく牌・物理ID等の部品です。
- 待ち分類固有の待ち・和了構成部品・待ち核など、およびシャンテン計算固有の手牌、容量・探索仕様は共通面子語彙と同じ概念ではありません。ローカルにあることだけを理由に共通化対象とは判断できません。

## ほかの対応関係・未決定候補

以下は調査時点の3リポジトリの宣言とAdapterを比較し、同じ概念または同じ写像を別の名前で
表している項目と、名前の整理が未決定の候補です。Coreの`Pair`と面子語彙は前節で決定
したため、残る識別子とAdapterの変更は後続の実装タスクで行います。

| 対応する名前 | 一致度・根拠 | 改名を検討する場合 |
|---|---|---|
| Core `Pair` ↔ 待ち分類 `Toitsu` | **同義対応。** どちらも同一牌種ちょうど2枚を表します。3枚・4枚の手牌中の同種牌は`TileCounts`に保持し、そこから2枚をPairとして分解します。Shantenの`pairCount`は2枚以上の牌種数であり、Pairの構造体ではありません。固定槓は手牌カウントとは異なる`FixedMeld.kan`です。 | 移行中は全値往復を使って対応を確認し、直接利用後は重複型と不要な往復証明を削除します。Shantenでは`pairCount`を牌種数を数える独自の計算として保ち、手の内の4枚カウントから固定槓へ変換しません。 |
| 待ち分類/Core `MentsuCandidate` ↔ 旧Shanten `Meld` | **順子・刻子形は対応し、Core API名はwait-classification側へ統一済み。** 候補は`.shuntsu`（共有`Shuntsu`）または`.koutsu`（牌種）です。旧Shantenの`.sequence`／`.triplet`も、副露状態を持たない同じ標準形でした。 | CoreとShantenの移行は完了済みです。待ち分類もCore型の直接利用へ移し、順序付き展開・列挙は分類側に残します。副露・槓を含むGo入力の`Meld`とは統合しません。 |
| Core/Shanten `Tile.suited` ↔ 待ち分類 `Tile.numbered` | **同じ牌種集合を指すが、注目点が異なる。** どちらもスートとランクで表す27種類の数牌で、adapterは直接対応させています。`.numbered`は数牌としての構造、`.suited`はスートを持つ牌としての構造を前面に出します。 | Coreの統一名はCoreの表現責務とwait-classificationでの命名意図を合わせて決めます。単にconsumer間で使われている数だけを根拠に`.suited`へ寄せず、どちらがCoreのwhatを最も明確に示すかを検討します。 |
| Core `Suit.man/pin/sou` ↔ 待ち分類 `Suit.Manzu/Pinzu/Souzu` | **同じスート要素。** 3つのスートが要素ごとに双方向対応し、adapterの往復定理があります。違いは略記と日本語ローマ字表記です。 | 公開名は改名可能です。`Manzu/Pinzu/Souzu`を含む候補を代表コードで比較し、Core内の順序・表記仕様と整合させて決定します。 |
| Core `Int37Index.tile` ↔ 旧Shanten `Input37.normalizeTile`、および Core `Tile.int37Index` ↔ 旧Shanten `Input37.normalIndex` | **同じ写像（移行済み）。** 前者は37スロットから牌種へ、後者は牌種からInt37スロットへ写します。Shanten側wrapperは削除され、Core写像を直接使います。 | Go実装もCoreのスロット順・容量・赤5規約に追随します。 |
| Core `aggregateInt37` ↔ 旧Shanten `Input37.normalizeCounts` | **同じ集約（移行済み）。** 同じ37枠の符号付きカウントを、赤5を通常5へまとめた牌種カウントへ集約します。Shanten側wrapperは削除され、Core関数と定理を直接使います。 | Coreを語彙・演算の正本とし、consumerだけに同じ集約定義を残しません。 |
| Core `Int37Counts` ↔ 旧Shanten Lean `Input37.Counts37` | **完全一致（移行済み）。** Shanten LeanはCoreの`Int37Counts`を直接使い、重複aliasを削除しました。Goの`Counts37`は固定長配列`[37]int`という別言語の表現ですが、意味上のスロット順・容量・赤5規約はCore定義に追随させます。 | Goではidiomaticな配列表現を維持しても構いませんが、別仕様として独立進化させずCoreの意味に追随します。 |
| Core `Tile.index` ↔ 待ち分類 `Tile.orderKey` | **値の対応は証明済み、用途に違いあり。** 共有`Fin 34`添字と分類側のソート用`Nat`について、`tileIndex_val`が値の一致を証明します。 | 牌種の安定順・indexはCoreの責務です。consumerはCore添字をソートキーとして使えるため、移行後はローカル`orderKey`定義を削除し、必要な箇所で添字の値を使います。 |
| Core `PhysicalTileId : Fin 136` ↔ 待ち分類 `PhysicalTile := Tile × Fin 4` | **同じ物理牌を表す別表現。** adapterは牌種とcopyを保存してCoreのTenhou順IDへ写します。Coreは赤5 copy 0を含む規約を所有し、consumerの型定義だけではその規約を表していません。 | Coreの`PhysicalTileId`を利用する方向です。まずadapterで現行Handモデルとの対応を証明し、物理牌型・変換・重複定義を消して直接Core型を使います。Int37/Int34の入出力・集計規則もCoreを正本とし、Goは同じ仕様に合わせます。 |
| Core `StandardCompletion` ↔ 待ち分類 `WinningPartitionSpec` / `IsStandardAgari` ↔ Shanten `Complete .mentsuHand` | **近縁だが同一ではない。** Coreはカウントと分解証人、待ち分類は牌リストと分割、Shantenは枚数制限・固定面子文脈を含みます。completionの証明形式・目的も異なります。 | ひとつの`Completion`へ無理に統合するのは後回しにします。`Standard` / `Special`だけでは意味が伝わらないため、Coreの仕様が何を保証するかを基に名前を再検討します。各consumerはCoreが定義するwhatを使い、固有の入力条件や計算方法は残します。 |

### 改名の優先順位

1. **決定済み・高:** Coreの共有面子型をwait-classification由来の`Shuntsu`／`MentsuCandidate`（`.shuntsu`／`.koutsu`）へ改名します。Adapterで意味対応を確認した後、consumerをCore定義へ移してlocal型・移行Adapterを削除します。API互換aliasは必須ではありません。
2. **決定済み・高:** Core `Pair`は厳密に2枚として維持し、既存`TileCounts`の同種牌カウントからPairを取り出すモデルにします。`Toitsu`との全値往復は移行中の対応確認に使います。4枚固定の`Kan`は手の内の4枚カウントとは別型・別状態として扱います。
3. **中:** Shanten `Hand`は`HandState`等の抽象状態を表す名へ改名し、待ち分類の具体的な手牌型とは区別します。wait-classificationの`Hand`は物理牌を持つconsumer固有モデルとして維持し、必要なら`ConcreteHand`を検討します。
4. **中:** `pairCount`の種類数意味を明確にする改名、Coreが持つ物理牌／Int37／Int34定義の直接利用、Go実装のCore仕様追随を行います。移行用adapterは置換が完了した範囲から削除します。
5. **後回し／条件付き:** `Completion`のconsumer横断統一は条件・目的が異なるため保留し、Core仕様の保証内容に基づく名前を再設計します。`IsTenpai`は待ち分類が通常形だけを扱う文脈では自然で、Shantenのtenpai値と修飾して区別します。`WaitWitness`は任意の明確化案、`WaitCore`は意図的な用語として改名せず維持します。

推奨する移行は、(1) Coreのwhat・語彙を確定、(2) local型とのadapterと対応証明を追加、
(3) consumerの処理をCore型へ段階的に切替、(4) local定義・移行adapterを削除、です。
互換性エイリアスの維持を前提としないため、最後は単一の共有定義へ収束できます。

## 同じ語の意味衝突

ここでは同じ名前が異なる型・プロジェクトで異なる範囲を指すケースを挙げます。
「意味が違う」には、概念そのものが違う場合と、同じ概念の異なる抽象レベル・証拠形式を
指す場合があります。前者は型名の明確化を優先し、後者は文書・修飾語による区別を基本とします。

| 語 | 用法ごとの意味 | 誤読リスクと改名案 |
|---|---|---|
| **Meld / 面子** | Goの[`Meld`](../mahjong-shanten-calculation/shanten.go)は固定済みの入力セットで、`Chi`・`Pon`・`Ankan`・`Daiminkan`・`Kakan`と全牌カウントを持ちます。Lean共有・Shantenの旧`Meld`、現在の[`MentsuCandidate`](../mahjong-domain-core/MahjongDomain/Parts.lean)は3枚の順子／刻子という形だけで、副露状態や槓は表しません。Shantenの`Capacity.FixedMeld`は固定文脈として形または槓を包みます。 | **改名先決定済み。** Goの固定セット契約`Meld`は維持し、Core/Leanの標準形候補は`MentsuCandidate`（`.shuntsu`／`.koutsu`）とします。Go実装の牌表現・挙動はCore仕様に追随させます。 |
| **Hand / 手牌** | 待ち分類の[`Hand`](../mahjong-wait-classification/Mahjong/Hand.lean)は重複しない物理牌の有限列で、枚数は1/4/7/10/13枚です。Shantenの[`Hand`](../mahjong-shanten-calculation/Shanten/Core.lean)は正規化牌種カウントと固定面子数だけを持つ抽象状態で、物理牌や固定面子の牌内容は持ちません。Goの`Input`は手牌相当の要求値で、`Standing`と`Melds`を分けます。 | **高。** Shanten型は`HandState`等の名が候補です。`AbstractHand`は避けます。待ち分類の`Hand`は物理牌を持つconsumer固有モデルで共有化しにくいため、現状名を維持するか、他文脈との混同が実際に問題となれば`ConcreteHand`を検討します。Goの`Input`は境界要求の名前として妥当です。`Standing`は暗槓も除いた手元牌を指す意図的な用語であり、`concealed hand`や非一般的な`Fixed/NonFixed`へ変える理由はありません。 |
| **Pair / 対子・雀頭・pair count** | Coreの現在の[`Pair`](../mahjong-domain-core/MahjongDomain/Parts.lean)は厳密に2枚です。改定後も意味を維持し、`TileCounts`から同種牌を2枚Pairとして分解します。手の内の4枚は4枚の牌カウントであり、固定された槓ではありません。`Toitsu`とShantenの`Taatsu.pair`も2枚、[`pairCount`](../mahjong-shanten-calculation/Shanten/Core.lean)は「2枚以上ある牌種の種類数」で、七対子の7対とも別概念です。固定槓は`Capacity.FixedMeld.kan`で表します。 | **意味・範囲決定済み。** `Toitsu`とCore `Pair`は同じ2枚概念として全値対応させます。`pairCount`は牌種数を数える別の計算として維持します。`TileCounts`の枚数条件、Pairへの分解、固定槓をそれぞれ区別します。 |
| **Complete / Completion / 完成** | Coreの現行`StandardCompletion`は、指定カウントと面子数に一致する分解証人を持つ`Prop`です。待ち分類の[`WaitCompletion`](../mahjong-wait-classification/Mahjong/WaitCompletion.lean)は待ち牌と和了構成部品列のデータです。Shantenの[`Complete`](../mahjong-shanten-calculation/Shanten/Specification.lean)は形別の構造条件で、枚数制限等も含みます。Goの結果値では完成時のシャンテンが`-1`です。 | **中。** 目的・証拠形式が異なるため無理な共通名化は後回しです。Core名の`StandardCompletion`も「何がstandardか」を説明で調べさせるため、保証内容を基に再検討します。`Standard` / `Special`を安易に追加せず、Coreのwhatとconsumerの条件・計算法を分けます。 |
| **Tenpai / テンパイ** | 待ち分類の[`IsTenpai`](../mahjong-wait-classification/Mahjong/WaitCompletionFinder.lean)は、合法な通常形牌姿に通常形待ちが少なくとも1つあることです。Shantenのtenpaiは構造距離に基づく`shanten = 0`で、総合値では七対子・国士無双も候補です。 | **文脈差として正常。** 待ち分類が通常形のみを対象とする前提では`IsTenpai`は適切です。Shantenの値との同一性は主張せず、「通常形待ち」と「Shanten値0」を明記します。 |
| **Wait / 待ち** | 待ち分類の[`Wait`](../mahjong-wait-classification/Mahjong/WaitCompletionFinder.lean)は、候補牌と`IsWaitFor`証明を一体にした値です。`waitingTiles`は候補牌の列挙、`WaitCompletion.wait`と`WaitCore.wait`はその牌種値を保持します。 | **中。** 候補牌、証拠、列挙処理が同じ語根で現れます。`Wait`は証拠型であることを文書では明示し、改名する場合は`WaitWitness`が候補です。フィールド`wait`は牌種を保持するため、`waitTile`の方が自己説明的です。既存のnamespaceとコメントで区別できる場合、即時改名の必要性は低いです。 |
| **Core / core** | `mahjong-domain-core`のCoreは共有ドメインライブラリです。一方、待ち分類の[`WaitCore`](../mahjong-wait-classification/Mahjong/WaitDecompositionCode.lean)は待ち牌と残存成分列の組で、数学的なkernelとは異なる分類用語です。`WaitCoreExtraction.core`は抽出後に残った成分列を指します。 | **改名不要。** `WaitCore`は意図して選ばれた分類語彙として維持します。説明ではCoreライブラリと待ち核を区別します。`CoreUtils`等はライブラリ／リポジトリの名前として必要性が確認された場合に限り別途検討します。 |
| **Tile / Tiles / 牌** | Leanの`Tile`は3プロジェクトとも原則として正規化された牌種です。物理的な1枚は待ち分類の`PhysicalTile`や共有の`PhysicalTileId`で別表現です。一方Goの`Meld.Tiles`は牌の列でなく、赤5を分ける`Counts37`カウントベクトルです。 | **中。** Coreが物理牌・Int37/Int34仕様を担い、Goも意味を追随します。Goフィールド`Tiles`はカウント配列だとコメントで明示し、公開API改名が自然な機会に`TileCounts`等を検討します。 |

### 同名語の対応方針

- 意味範囲が異なる`Meld`、`Hand`は、consumerのプログラム上の役割に沿って改名・修飾します。`Tenpai`は対象範囲を明記すれば現行名で問題ありません。
- `Pair`は厳密に2枚のままとし、`TileCounts`の同種牌カウントから分解します。手の内の3枚・4枚、固定槓、`pairCount`はそれぞれ別概念として扱います。
- `WaitCore`は分類固有の確立した語として維持します。`Wait`を`WaitWitness`へ改名するのは任意の明確化で、優先度は低めです。
- `Completion`は無理に単一名へ統一せず、Coreの保証内容を表す命名を別途検討します。今回は識別子・APIを変更せず、決定したモデルと移行方針を本書に記録しました。

## Lean以外の公開型について

GoコードがLeanの型をimportする構成ではありませんが、Tenhou/Int37/Int34の意味・
インデックス順・容量・赤5規則はCoreを正本としてGo実装が追随する方針です。
Goの`Counts37 [37]int`のような言語に適した表現は維持できます。

Goの[`Meld`](../mahjong-shanten-calculation/shanten.go)はchi・pon・ankan・daiminkan・
kakan等の固定済みセットを表す契約型で、Leanの面子形とは意図的に異なります。
Goの`Meld.Tiles`はそのセットが占有する牌のInt37カウントです。Go名の維持・改名は
公開契約として別に判断しますが、内容・正規化規則をCoreと独立した定義にしないようにします。

## 移行可能性と作業計画

### 着手可否

**Core APIは実装済みです（Lean build確認済み）。** 共有面子API、厳密な2枚としての`Pair`、
`TileCounts`からのPair分解、手の内4枚と固定槓の区別をCoreの型・定理に反映しました。
`Completion`の統一・改名は独立した後続課題とし、今回の移行を止めません。互換性aliasは
前提にしません。

これはW0〜W7で完了した共通核の導入・接続をやり直す計画ではなく、W7後に残った
consumer側の同義定義とAdapterを、決定したCore APIへ段階的に移す後続計画です
（[W7までの計画](../mahjong-shanten-calculation/docs/project/SHARED_DOMAIN_EXTRACTION_PLAN_2026-11-17.md)、
[残存候補一覧](../mahjong-shanten-calculation/docs/project/CORE_EXTRACTION_CANDIDATES_2026-11-20.md)）。
以前の計画にあるLean consumer API維持の前提より、共有語彙の直接利用と
重複の解消を優先し、互換aliasなしの改名を許容します。分類の出力順・結果、
意味上の保証、Goの公開契約は引き続き維持します。

### 段階

1. **[完了] Coreの共有APIを実装する。**
   - `Meld`を`MentsuCandidate`へ置き換え、共有`Shuntsu`と`.shuntsu`／`.koutsu`
     constructorを定義しました。`MentsuCandidate.tiles`、`MentsuCandidateList`の展開・集約、
     `StandardDecomposition`の分解定理も新APIへ揃えました。
   - `Pair`と`Pair.tiles`は厳密に2枚のまま維持し、`Pair.counts_eq_pair_add_remaining`で
     `TileCounts`からPairを選び、残余と合わせて元のカウントを再構成できることを証明しました。
     3枚・4枚を`Pair`へ格納する型や、手の内の4枚を`Kan`に変換する仕組みは追加していません。
   - `TileCounts`は汎用カウントとして保ち、物理牌上限4は有効な手牌・表現の制約として
     別に扱います。`Kan`は固定4枚の独立した意味を保ちます。
   - **検証:** 標準形候補の展開が3枚、Pair展開が2枚、カウントの再構成が成立し、
     固定`Kan`の占有枚数が4枚であることを、一時作業コピーでの`lake build --wfail`で確認しました。
     Pair分解は`TileCounts`上で行い、固定`Kan`と同一視する変換は定義していません。

2. **wait-classificationを移行する。**
   - `PartsAdapter.lean`の面子候補対応を、旧Core `Meld`から`Shuntsu`／
     `MentsuCandidate`へ切り替えました。`Toitsu`↔Core `Pair`と面子候補の全値往復、
     constructor・牌カウント対応証明を維持しています。通常形完成の接続証明も新Core
     `StandardDecomposition.mentsuCandidates`に追随しました。
   - **現状:** 分類の列挙・順序付き牌列処理はローカルな部品型を使い、Adapterが
     共有完成仕様との証明境界を担っています。**移行先:** Core型を直接使い、
     順序付き`List`展開・列挙など分類固有の操作を分類側に残します。Coreの
     `Multiset`との対応を証明し、結果順・重複数は別途検証します。
   - 分類固有の待ち分解、`WaitCore`、物理的`Hand`はローカルに残します。
     `DomainAdapter`も牌・物理牌など未移行の対応に必要な間は残し、Parts移行だけで
     一括削除しません。
   - 分類の牌列順、候補列挙順、分類ID・結果は変えません。Coreの`Multiset`を導入する
     ためだけに、順序付き`List Tile`の出力表現を置き換えません。
   - **完了条件:** 対象の`Toitsu`、`Shuntsu`、`MentsuCandidate`はCore型を直接
     利用し、重複型と不要な`PartsAdapter`変換・往復証明を削除すること。残る例外は
     理由と解消条件を記録し未完了として扱うこと。順序付き展開とCore展開の対応証明、
     列順・結果・重複数の回帰検査、対象宣言の不在検査を追加し、
     `lake build Mahjong MahjongTests`を通すこと。Go連携がある変更では
     `go test ./mahjong`も通すこと。代表処理の読解負荷比較と人による確認も記録すること。

3. **Shantenの基礎型・証明を移行する。完了。**
   - 牌種・スート・カウントと面子候補をCore型へ直接置換し、`pairTiles`を
     Core `Pair.tiles`に基づけました。探索状態・分解・列挙・正当性、
     容量付き固定文脈とInt37の変換・検証証明を更新しました。
   - `Capacity.FixedMeld.kan`はCoreの固定槓占有を用い、手の内のカウントと
     区別します。`pairCount`は2枚以上ある牌種の種類数のままです。`Hand`、
     `Taatsu`、容量・探索方針などShanten固有モデルは維持しました。
   - 不要になったShanten側の型変換Adapterを削除し、通常完成の対応定理を
     `Specification.lean`で直接証明しました。待ち分類との固定文脈連携も追随しました。
     `Input37`の`Counts37` aliasと正規化・容量wrapperはステップ5で削除しました。
   - **検証:** 書き込み可能な隔離ビルドでShantenの`lake build`と固定文脈連携
     `w6`の`lake build`が成功し、標準完成・Pair対応を含む`sorryAx`検査と
     既存の探索・固定槓・入力回帰例が通りました。

4. **Go契約をCore仕様と照合する。**
   - Goの`Meld`は固定済み入力契約として維持し、Leanの`MentsuCandidate`へ改名・統合
     しません。standing countsと固定槓の占有枚数・容量制約がCoreの牌表現と一致することを
     確認します。
   - **完了条件:** 差分がある場合は境界テストを追加し、`go test ./...`と`go vet ./...`
     を通します。Goに対応する数値テストがない場合、`go test`はビルド確認に留まることを
     明記します。

5. **移行用Adapter・重複を片付け、文書を揃える。**
   - Core型へ直接切り替わり、往復・意味対応証明が不要になった範囲からadapterとlocal型を
     削除します。未移行の表現変換に使うadapterや、consumer固有の状態・ロジックは残します。
   - **Shanten Lean側は完了。** Int37の重複alias・写像／容量／集約wrapperと、候補牌展開・
     カウント変換wrapperを削除し、Core APIを直接使うよう更新しました。wait-classification側の
     local型・Adapter整理は未完了です。Goとの照合は後続で行います。
   - glossary、API説明、移行状況を実装に合わせて更新し、`Completion`は現行仕様のまま
     別課題として記録します。
   - **完了条件:** Coreとconsumerで同じwhatを表す重複型が対象範囲に残らず、利用中の
     変換・証明が残作業またはconsumer固有の理由と結び付いていること。Coreとconsumerの
     Lean build、wait-classificationのLeanテスト、該当するGo検査が成功すること。

### 依存関係とリスク

順序は **Core →（wait-classification、Shantenを並行移行可能）→ adapter整理** です。
Go照合はCoreの表現規則が確定した後ならLean移行と並行できます。Shantenは`Meld`・
`pairTiles`を参照する証明が多数の`MentsuHand`／`Capacity`モジュールへ広がるため、
Core定理を先に固定し、基礎型から下流へ小刻みに移すのが主なリスク対策です。
`Completion`の意味統一はこの依存グラフに含めません。
