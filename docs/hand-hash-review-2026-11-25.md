# hand-hash 実装レビュー

レビュー日: 2026-11-25  
対象: `mahjong-hand-hash` (`4559a77`)  
参照: [牌姿の双方向キー計画](./hand-perfect-hash-plan.md)

## 要約

現状の実装は実験段階であり、永続キーとして利用できない。複数の固定面子を持つ鳴き込みキーで、異なる牌姿が同じキーになる衝突を再現した。加えて、牌集合キーと鳴き込みキーが型レベルで区別されず、64ビット範囲と双方向性の保証も未完了である。

## 指摘事項

### [P1] 複数固定面子の組rankに衝突がある

[`fixedComboRankFrom` と `fixedComboUnrank`](../mahjong-hand-hash/MahjongHandHash/HandKey.lean) は複数固定面子の組を番号付けするが、rank側とunrank側の組合せ数の数え方が整合していない。rankは同じ面子番号の重複を許す一方、unrankの各ブロック長は `fixedWays (head + 1) ...` で現在の番号と同じ面子を次の位置に置く場合を数え落とす。

修正前の実装で次の異なる入力を評価すると、どちらも `4244394020351` になった。

- 手牌 `456789m1p`、`123m` の2mを鳴いたチー2組
- 同じ手牌、`123m` の1mを鳴いたチー1組と中の暗槓1組

この衝突は鳴き込みキーの単射性を直接破り、decodeして元の牌姿を一意に復元できないため、修正前の実装は鳴き込みキーとして利用できなかった。

**対応済み:** rank側・unrank側とも、次の面子番号が現在の番号と同じ場合をブロック数に含めるよう修正した。上記2入力のキーが異なること、および重複するチー組のencode/decode往復を回帰テストに追加し、`lake build MahjongHandHash MahjongHandHashTests` の成功を確認した。完全な単射性・往復証明など、P2の指摘は未解決である。

### [P2] 2つのキー空間がLean上で区別されない

[`TileCollectionKey` と `MeldedHandKey`](../mahjong-hand-hash/MahjongHandHash/HandKey.lean) はどちらも `abbrev ... := Int` である。そのため、牌集合キーを `MeldedHand.decode` に渡す、または鳴き込みキーを `TileCollection.decode` に渡すコードが型検査を通り、異なる空間のキー同士もそのまま比較できる。

仕様では両キー空間を別扱いにし、相互比較を禁止している。内部表現として `Int` を使う場合でも、公開APIでは別の構造体または不透明型にし、必要な整数変換を明示させるべきである。

### [P2] INT64範囲と可逆性の契約が実装で保証されていない

[`fixedKeyLimit`](../mahjong-hand-hash/MahjongHandHash/HandKey.lean) は定義されているが使われていない。両方のencodeはキー値を `Int.ofNat` で返すのみで、符号付き64ビット上限との照合を行わない。また、実装にはencode/decodeの往復、単射性、全出力の範囲を示す証明がなく、現在のテストにもこれらの全域保証はない。

候補数の見積りが `2^63` 未満であることだけでは、実装したrank/unrankと出力値の契約を証明したことにならない。永続化を許可する前に、計画書の受け入れ条件にある証明または同等の厳密な検証を完了し、テストベクトルを固定する必要がある。

## 検証

- `lake build MahjongHandHash MahjongHandHashTests` は成功した。Coreの `MahjongDomain/Parts.lean` からlint警告が出たが、今回のレビュー対象のビルド失敗ではない。
- 上記の衝突例は修正前に `lake env lean --stdin` で両入力をencodeして確認した。
- 現在の [`HandKey` テスト](../mahjong-hand-hash/MahjongHandHashTests/HandKey.lean) はコンパイル時の評価例と基本的な往復例を含むが、複数固定面子の順位付け、2キー空間の取り違え、INT64上限を検査していない。

## 判定

P1の衝突を修正し、P2の型分離と保証不足を解消するまでは、解析結果を保存する永続キーとして公開・使用しないこと。
