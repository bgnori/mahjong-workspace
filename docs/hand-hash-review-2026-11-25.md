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

レビュー時の [`TileCollectionKey` と `MeldedHandKey`](../mahjong-hand-hash/MahjongHandHash/HandKey.lean) はどちらも `abbrev ... := Int` だった。そのため、牌集合キーを `MeldedHand.decode` に渡す、または鳴き込みキーを `TileCollection.decode` に渡すコードが型検査を通り、異なる空間のキー同士もそのまま比較できた。

仕様では両キー空間を別扱いにし、相互比較を禁止している。内部表現として `Int` を使う場合でも、公開APIでは別の構造体または不透明型にし、必要な整数変換を明示させるべきである。

**部分対応:** 牌集合キーは`TileCountsKey`という別の構造体になった。鳴き込みキーの別型化は未対応である。

### [P2] INT64範囲と可逆性の契約が実装で保証されていない

**対応済み（実行時契約検査）。** 両方のencodeは、算出値が `fixedKeyLimit` 以下であることを確認し、decodeした結果が入力と同じ牌姿（鳴き込みキーでは固定面子順を正規化）に戻る場合のみ成功する。両方のdecodeも負値・`fixedKeyLimit` 超過を拒否し、成功結果を再encodeした値が入力キーと一致することを確認する。検査に失敗した場合は `roundTripFailure` または `keyOutOfRange` を返す。

回帰テストでは両キー空間の計算上限がINT64内であることと、INT64最大値を超えるdecodeの拒否を確認する。全域のLean定理そのものは未実装だが、APIは個々の呼び出しで範囲と往復を検査するため、未検査値を成功として返さない。なおencode時にdecodeも実行するため、検査コストが加わる。

## 検証

- `lake build MahjongHandHash MahjongHandHashTests` は成功した。Coreの `MahjongDomain/Parts.lean` からlint警告が出たが、今回のレビュー対象のビルド失敗ではない。
- 上記の衝突例は修正前に `lake env lean --stdin` で両入力をencodeして確認した。
- [`HandKey` テスト](../mahjong-hand-hash/MahjongHandHashTests/HandKey.lean) は両キー空間の上限とINT64超過キーの拒否を検査する。エンコード成功時の逆変換検査はAPI内で行う。

## 判定

P1の衝突とINT64・実行時可逆性検査の指摘は対応済み。P2の型分離は未対応であり、初版番号付けの正式な版固定や全域定理も未完了のため、解析結果を保存する永続キーとしての公開・使用は引き続き保留する。
