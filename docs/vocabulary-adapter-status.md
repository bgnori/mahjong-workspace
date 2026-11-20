# 共有ドメイン語彙とAdapterの現状

調査日: 2026-11-20

## 要約

3リポジトリには、牌・対子・面子に相当する語彙のローカル定義が
それぞれ残っています。`mahjong-domain-core`には共有Lean定義があり、待ち分類・
シャンテン計算にも意味対応を確認するAdapterと証明があります。ただし現在のAdapterは
主に段階移行のための境界であり、最終的にはCoreの定義を直接使ってconsumer側の重複定義・
Adapterをなくす方針が妥当です。

Coreが「何であるか（what）」を定義し、consumerがそれを用いた探索・分類・評価など
「どう使うか（how）」を定義します。公開API名の改名に互換性エイリアスは要らない前提で
進められますが、同じ語を不用意に一対一対応させず、概念の意味を確認してから統合します。

Tenhou物理牌、Int37、Int34の表現・変換・容量規則はCoreが責任を持つ対象です。
consumerはCoreの表現上で必要な処理を定義し、Go実装もそのCore仕様に追随します。

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

**方針:** 副露を表さないLeanの面子形に`Meld`という公開名を使わないようにします。
共有型には`MentsuShape`が有力です。これは副露状態ではなく、手牌構造の候補である
順子・刻子の形を表します。Goの固定済み`Meld`は入力境界の契約として別の概念なので、
名前を残すかは別途扱います。

constructorの語も一律に同義語として統合しません。待ち分類の`.shuntsu`／`.koutsu`は
手牌構造内の面子を表す立場、`.sequence`／`.triplet`は牌同士の連続・同種関係を述べる
立場として使い分けられるなら、別の概念として保ちます。Coreで共有するのは構造モデル
そのものであり、関係を表す述語・補助概念は実際に必要な場合だけ定義します。

公開APIの改名は許容され、歴史的互換性のための別名を維持する必要はありません。
ただし、意味対応を確認するAdapterと証明を先に置き、consumerがCore型を直接使うよう
移行した後で、重複定義と移行用Adapterを削除するのが安全です。

## リポジトリごとの定義とAdapter

| リポジトリ | ローカル／共有語彙 | Adapterの有無と範囲 |
|---|---|---|
| [mahjong-domain-core](../mahjong-domain-core/) | 共有定義の正本。現状は`Tile`、厳密に2枚を表す`Pair`、順子／刻子形の`Meld`、`Kan.occupiedTiles`、`StandardDecomposition`、`StandardCompletion`を定義します。`Meld`は副露状態を持たず、今後`MentsuShape`等へ改名する方針です。`Pair`も雀頭限定・2枚限定の現状モデルを再検討します。 | consumer向けAdapterはありません。共通の意味は[Parts.lean](../mahjong-domain-core/MahjongDomain/Parts.lean)と[用語集](../mahjong-domain-core/docs/GLOSSARY.md)に集約されています。Core自身のモデルの意味・名前も見直し対象です。 |
| [mahjong-wait-classification](../mahjong-wait-classification/) | [Basic.lean](../mahjong-wait-classification/Mahjong/Basic.lean)に`Suit`、`Honor`、`Tile`、独自の`PhysicalTile`等、[Pattern.lean](../mahjong-wait-classification/Mahjong/Pattern.lean)に意図を持って命名された`Toitsu`、`Shuntsu`、`MentsuCandidate`があります。待ち分解・待ち核などはこのプロジェクト固有で、共有しない分類ロジックです。 | **あり（移行用）。** 現在の`DomainAdapter.lean`／`PartsAdapter.lean`で対応を証明しています。移行時はCore定義の利用へ切り替え、同じ概念のlocal定義とAdapterを最終的に削除します。待ち分類で吟味済みの語は、共有名を決める際の有力な指針です。 |
| [mahjong-shanten-calculation](../mahjong-shanten-calculation/) | [Core.lean](../mahjong-shanten-calculation/Shanten/Core.lean)に独自の`Suit`、`Tile`、`TileCounts`、副露を意味しない`Meld`、牌multiset関数があります。`Hand`はカウントと固定面子数だけを持つ抽象状態です。`Capacity.FixedMeld`は標準形または槓を固定文脈として持ちます。 | **あり（移行用）。** [`DomainAdapter.lean`](../mahjong-shanten-calculation/Shanten/DomainAdapter.lean)が牌・カウント・面子・完成仕様を接続し、`Input37`の一部写像もCoreへ委譲しています。Core定義へ直接移行した後、重複型・wrapper・Adapterを整理する対象です。 |

## 重複と意味差

- 牌種・スート・牌種カウント、牌表現、面子形などの重複定義がconsumerに残っています。現Adapterは意味対応の証拠として有用ですが、最終的な重複解消ではCore型へ直接移行し、local宣言と移行用Adapterを削除します。
- 既存`Toitsu`↔`Pair` adapterの往復定理は、現在のCore `Pair`が「ちょうど2枚」と定義されるから成立しています。Core `Pair`の意味を複数枚同種牌の集まりへ広げるなら、`Toitsu`はその2枚ケースへの写像となり、全値に対する全単射ではなくなります。
- `MentsuCandidate`と`Meld`は現状の集合として対応しますが、`Meld`という共有名は副露と誤読されるため改名対象です。`shuntsu/koutsu`と`sequence/triplet`は手牌構造と牌同士の関係を区別できる場合に別概念として使います。
- シャンテンの`Hand`は共通の物理牌手ではなくカウント状態です。待ち分類の物理的`Hand`はconsumer固有で共有化しにくく、Coreに移す対象は`Hand`そのものではなく牌・物理ID等の部品です。
- 待ち分類固有の待ち・和了構成部品・待ち核など、およびシャンテン計算固有の手牌、容量・探索仕様は共通面子語彙と同じ概念ではありません。ローカルにあることだけを理由に共通化対象とは判断できません。

## ほかの同義語・別名の候補

以下は3リポジトリの宣言とAdapterを比較し、同じ概念または同じ写像を別の名前で
表している候補です。推奨は名前の整理案であり、この調査では識別子を変更していません。

| 対応する名前 | 一致度・根拠 | 改名を検討する場合 |
|---|---|---|
| Core `Pair` ↔ 待ち分類 `Toitsu` | **同義とは未確定。** `Toitsu`は同一牌種2枚の形です。現在のCore `Pair`も`Pair.tiles = replicate 2`でちょうど2枚ですが、Coreの`Pair`は雀頭として使う役割に寄っています。設計方針としてCoreの`Pair`は、雀頭の役割に限定せず、刻子・4枚組などに含まれる同種牌のまとまりも表せる概念へ広げる意向です。 | `Toitsu`はCore `Pair`の全別名ではなく、一般化された`Pair`の2枚ケースとなる可能性があります。CoreモデルでPairの要素数をどう表すか（許容範囲、2枚部分組か同種牌グループか）を先に定義し、既存adapterは全単射ではなく埋め込み・部分対応として書き直します。 |
| 待ち分類 `Shuntsu` / `.shuntsu`・`.koutsu` ↔ Core/Shanten `.sequence`・`.triplet` | **同じ値としての単純な同義語とは扱わない。** 待ち分類の語は手牌構造の面子として慎重に付けられています。一方`.sequence`／`.triplet`は牌同士の連続・同種関係を表す語として使い分けられる余地があります。現adapterは現在のconstructor値の対応を示しますが、意味上の区別を消す根拠にはなりません。 | `MentsuShape`を手牌構造の共通型とするなら、`.shuntsu`／`.koutsu`を構造constructorにする方向が候補です。`.sequence`／`.triplet`は別の関係述語・関係概念が必要な場合だけ使い、同じ型へ冗長な別名constructorを設けません。迷った場合はwait-classificationの吟味済み語彙を優先します。 |
| Core/Shanten `Tile.suited` ↔ 待ち分類 `Tile.numbered` | **同じ牌種集合を指すが、注目点が異なる。** どちらもスートとランクで表す27種類の数牌で、adapterは直接対応させています。`.numbered`は数牌としての構造、`.suited`はスートを持つ牌としての構造を前面に出します。 | Coreの統一名はCoreの表現責務とwait-classificationでの命名意図を合わせて決めます。単にconsumer間で使われている数だけを根拠に`.suited`へ寄せず、どちらがCoreのwhatを最も明確に示すかを検討します。 |
| Core `Suit.man/pin/sou` ↔ 待ち分類 `Suit.Manzu/Pinzu/Souzu` | **同じスート要素。** 3つのスートが要素ごとに双方向対応し、adapterの往復定理があります。違いは略記と日本語ローマ字表記です。 | 公開名は改名可能です。名前の明瞭さで迷う場合はwait-classificationの`Manzu/Pinzu/Souzu`を優先候補とし、Core内の順序・表記仕様と整合させます。 |
| Core `Int37Index.tile` ↔ Shanten `Input37.normalizeTile`、および Core `Tile.int37Index` ↔ Shanten `Input37.normalIndex` | **同じ写像。** 前者は37スロットから牌種へ、後者は牌種からInt37スロットへ写します。Shanten側の関数はCore写像を利用するwrapperです。 | CoreがTenhou/Int37/Int34を所有する方針に従い、consumerはCoreのrepresentationを直接利用します。意味確認用adapterは移行中のみ残し、利用側wrapper・重複名は直接移行後に削除します。Go実装もCoreのスロット順・容量・赤5規約に追随します。 |
| Core `aggregateInt37` ↔ Shanten `Input37.normalizeCounts` | **同じ集約。** 同じ37枠の符号付きカウントを、赤5を通常5へまとめた牌種カウントへ集約します。Shanten wrapperは共有関数を呼び、性質もCore定理へ接続しています。 | 消費側がCoreのInt37/Int34操作を直接使う形へ移行し、wrapperを削除します。Coreを語彙・演算の正本とし、consumerだけに同じ集約定義を残しません。 |
| Core `Int37Counts` ↔ Shanten Lean `Input37.Counts37` | **完全一致（型alias）。** `Input37.Counts37`は`MahjongDomain.Int37Counts`のabbrevです。Goの`Counts37`は固定長配列`[37]int`という別言語の表現ですが、意味上のスロット順・容量・赤5規約はCore定義に追随させます。 | Lean consumerではCoreの型を直接使い、重複aliasを移行後に削除します。Goではidiomaticな配列表現を維持しても構いませんが、別仕様として独立進化させずCoreの意味に追随します。 |
| Core `Tile.index` ↔ 待ち分類 `Tile.orderKey` | **値の対応は証明済み、用途に違いあり。** 共有`Fin 34`添字と分類側のソート用`Nat`について、`tileIndex_val`が値の一致を証明します。 | 牌種の安定順・indexはCoreの責務です。consumerはCore添字をソートキーとして使えるため、移行後はローカル`orderKey`定義を削除し、必要な箇所で添字の値を使います。 |
| Core `PhysicalTileId : Fin 136` ↔ 待ち分類 `PhysicalTile := Tile × Fin 4` | **同じ物理牌を表す別表現。** adapterは牌種とcopyを保存してCoreのTenhou順IDへ写します。Coreは赤5 copy 0を含む規約を所有し、consumerの型定義だけではその規約を表していません。 | Coreの`PhysicalTileId`を利用する方向です。まずadapterで現行Handモデルとの対応を証明し、物理牌型・変換・重複定義を消して直接Core型を使います。Int37/Int34の入出力・集計規則もCoreを正本とし、Goは同じ仕様に合わせます。 |
| Core `StandardCompletion` ↔ 待ち分類 `WinningPartitionSpec` / `IsStandardAgari` ↔ Shanten `Complete .mentsuHand` | **近縁だが同一ではない。** Coreはカウントと分解証人、待ち分類は牌リストと分割、Shantenは枚数制限・固定面子文脈を含みます。completionの証明形式・目的も異なります。 | ひとつの`Completion`へ無理に統合するのは後回しにします。`Standard` / `Special`だけでは意味が伝わらないため、Coreの仕様が何を保証するかを基に名前を再検討します。各consumerはCoreが定義するwhatを使い、固有の入力条件や計算方法は残します。 |

### 改名の優先順位

1. **高:** Coreの非副露面子型`Meld`を`MentsuShape`等へ改名し、Core what／consumer howの境界を明確にする。現在のAdapterで意味対応を確認した後、consumerをCore定義へ移してlocal型・移行Adapterを削除します。API互換aliasは必須ではありません。
2. **高（モデル再設計を含む）:** Core `Pair`を雀頭・ちょうど2枚に限定しない概念へ見直します。これに伴い`Toitsu`との対応を全単射とみなさず、2枚ケースの埋め込みとして再定義します。
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
| **Meld / 面子** | Goの[`Meld`](../mahjong-shanten-calculation/shanten.go)は固定済みの入力セットで、`Chi`・`Pon`・`Ankan`・`Daiminkan`・`Kakan`と全牌カウントを持ちます。Lean共有・Shantenの[`Meld`](../mahjong-domain-core/MahjongDomain/Parts.lean)は3枚の順子／刻子という形だけで、副露状態や槓は表しません。Shantenの`Capacity.FixedMeld`は固定文脈として形または槓を包みます。 | **高。** 副露を表すGo名と副露を含まないLean型に同じ`Meld`を使うのは避けます。Lean側を`MentsuShape`へ改名し、Goの`Meld`は固定セット契約として保持します。Go実装の牌表現・挙動はCore仕様に追随させます。 |
| **Hand / 手牌** | 待ち分類の[`Hand`](../mahjong-wait-classification/Mahjong/Hand.lean)は重複しない物理牌の有限列で、枚数は1/4/7/10/13枚です。Shantenの[`Hand`](../mahjong-shanten-calculation/Shanten/Core.lean)は正規化牌種カウントと固定面子数だけを持つ抽象状態で、物理牌や固定面子の牌内容は持ちません。Goの`Input`は手牌相当の要求値で、`Standing`と`Melds`を分けます。 | **高。** Shanten型は`HandState`等の名が候補です。`AbstractHand`は避けます。待ち分類の`Hand`は物理牌を持つconsumer固有モデルで共有化しにくいため、現状名を維持するか、他文脈との混同が実際に問題となれば`ConcreteHand`を検討します。Goの`Input`は境界要求の名前として妥当です。`Standing`は暗槓も除いた手元牌を指す意図的な用語であり、`concealed hand`や非一般的な`Fixed/NonFixed`へ変える理由はありません。 |
| **Pair / 対子・雀頭・pair count** | Coreの現在の[`Pair`](../mahjong-domain-core/MahjongDomain/Parts.lean)は厳密に2枚で雀頭用途に寄っていますが、目指す意味は雀頭という役割や厳密な2枚数に限定されない同種牌のまとまりです。`Toitsu`は同一牌2枚の手牌構造です。Shantenの`Taatsu.pair`は未完成ブロック、[`pairCount`](../mahjong-shanten-calculation/Shanten/Core.lean)は「2枚以上ある牌種の種類数」で、七対子の7対とも別の概念です。 | **高（Coreモデル見直し）。** `Toitsu`と一般化した`Pair`を同義・全単射としません。`pairCount`は実際に牌種数を数えるため`pairKindCount`等へ改名する候補です。雀頭、搭子、七対子で「pair」がどの意味かを文脈化します。 |
| **Complete / Completion / 完成** | Coreの現行`StandardCompletion`は、指定カウントと面子数に一致する分解証人を持つ`Prop`です。待ち分類の[`WaitCompletion`](../mahjong-wait-classification/Mahjong/WaitCompletion.lean)は待ち牌と和了構成部品列のデータです。Shantenの[`Complete`](../mahjong-shanten-calculation/Shanten/Specification.lean)は形別の構造条件で、枚数制限等も含みます。Goの結果値では完成時のシャンテンが`-1`です。 | **中。** 目的・証拠形式が異なるため無理な共通名化は後回しです。Core名の`StandardCompletion`も「何がstandardか」を説明で調べさせるため、保証内容を基に再検討します。`Standard` / `Special`を安易に追加せず、Coreのwhatとconsumerの条件・計算法を分けます。 |
| **Tenpai / テンパイ** | 待ち分類の[`IsTenpai`](../mahjong-wait-classification/Mahjong/WaitCompletionFinder.lean)は、合法な通常形牌姿に通常形待ちが少なくとも1つあることです。Shantenのtenpaiは構造距離に基づく`shanten = 0`で、総合値では七対子・国士無双も候補です。 | **文脈差として正常。** 待ち分類が通常形のみを対象とする前提では`IsTenpai`は適切です。Shantenの値との同一性は主張せず、「通常形待ち」と「Shanten値0」を明記します。 |
| **Wait / 待ち** | 待ち分類の[`Wait`](../mahjong-wait-classification/Mahjong/WaitCompletionFinder.lean)は、候補牌と`IsWaitFor`証明を一体にした値です。`waitingTiles`は候補牌の列挙、`WaitCompletion.wait`と`WaitCore.wait`はその牌種値を保持します。 | **中。** 候補牌、証拠、列挙処理が同じ語根で現れます。`Wait`は証拠型であることを文書では明示し、改名する場合は`WaitWitness`が候補です。フィールド`wait`は牌種を保持するため、`waitTile`の方が自己説明的です。既存のnamespaceとコメントで区別できる場合、即時改名の必要性は低いです。 |
| **Core / core** | `mahjong-domain-core`のCoreは共有ドメインライブラリです。一方、待ち分類の[`WaitCore`](../mahjong-wait-classification/Mahjong/WaitDecompositionCode.lean)は待ち牌と残存成分列の組で、数学的なkernelとは異なる分類用語です。`WaitCoreExtraction.core`は抽出後に残った成分列を指します。 | **改名不要。** `WaitCore`は意図して選ばれた分類語彙として維持します。説明ではCoreライブラリと待ち核を区別します。`CoreUtils`等はライブラリ／リポジトリの名前として必要性が確認された場合に限り別途検討します。 |
| **Tile / Tiles / 牌** | Leanの`Tile`は3プロジェクトとも原則として正規化された牌種です。物理的な1枚は待ち分類の`PhysicalTile`や共有の`PhysicalTileId`で別表現です。一方Goの`Meld.Tiles`は牌の列でなく、赤5を分ける`Counts37`カウントベクトルです。 | **中。** Coreが物理牌・Int37/Int34仕様を担い、Goも意味を追随します。Goフィールド`Tiles`はカウント配列だとコメントで明示し、公開API改名が自然な機会に`TileCounts`等を検討します。 |

### 同名語の対応方針

- 意味範囲が異なる`Meld`、`Hand`は、consumerのプログラム上の役割に沿って改名・修飾します。`Tenpai`は対象範囲を明記すれば現行名で問題ありません。
- `Pair`はCoreの概念自体を再検討し、`Toitsu`との対応を再定義します。`pairCount`とGoの`Meld.Tiles`は実体を名前・コメントに反映させる候補です。
- `WaitCore`は分類固有の確立した語として維持します。`Wait`を`WaitWitness`へ改名するのは任意の明確化で、優先度は低めです。
- `Completion`は無理に単一名へ統一せず、Coreの保証内容を表す命名を別途検討します。今回は識別子・APIを変更せず、移行方針を文書に反映しました。

## Lean以外の公開型について

GoコードがLeanの型をimportする構成ではありませんが、Tenhou/Int37/Int34の意味・
インデックス順・容量・赤5規則はCoreを正本としてGo実装が追随する方針です。
Goの`Counts37 [37]int`のような言語に適した表現は維持できます。

Goの[`Meld`](../mahjong-shanten-calculation/shanten.go)はchi・pon・ankan・daiminkan・
kakan等の固定済みセットを表す契約型で、Leanの面子形とは意図的に異なります。
Goの`Meld.Tiles`はそのセットが占有する牌のInt37カウントです。Go名の維持・改名は
公開契約として別に判断しますが、内容・正規化規則をCoreと独立した定義にしないようにします。

## 残作業量の見立て

1. **Coreのモデル・語彙の確定が先です。** 非副露面子の新名称（`MentsuShape`が有力）、Pairの一般化された意味・多重度、Completionが保証する内容、物理牌とInt表現の責務をCoreで定義します。
2. **現adapterは移行の安全網として活用できます。** 現在のconsumer型とCore型の意味対応を証明し、同値なもの・部分埋め込みになるもの・意味が違うものを区分してからconsumer実装を切り替えます。
3. **consumerをCore定義へ直接移行します。** 既存名との互換性エイリアスは前提にせず、Coreがwhatを担い、待ち分類・シャンテン計算はそれぞれのhowと独自状態を担う構成にします。待ち分類の意図的な語彙をCore名の選定に活用します。
4. **置換できた範囲のlocal定義・adapterを削除します。** `Hand`のようにconsumer固有の状態モデルや待ち分類のWaitCoreは削除せず、Coreが所有すべき牌・物理ID・Int37/Int34等をconsumerで再定義しないよう整理します。
5. **GoもCoreの意味仕様に追随させます。** Goで必要な配列・構造体の表現は保ちつつ、Tenhou/Int37/Int34の変換と容量規則をCore仕様と一致させます。

したがって残作業は、既存adapterを増やすだけではなく、Coreの意味モデルを確定し、
証明を経てconsumerから重複定義と移行adapterを取り除き、Go実装を同じ仕様へ合わせる
段階移行です。公開API名の変更を許容するため、互換性aliasを維持する追加負担は不要です。
