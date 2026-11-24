# Lean回帰テストの階層化方針

制定日: 2026-11-24

## 目的と適用範囲

この方針は、mahjong workspace配下のLeanプロジェクトに共通して適用します。ローカルの編集・検証サイクルを短くしながら、網羅的な検査とその保証をCIから外さないことが目的です。

repoごとの実測値、対象モジュール、実行コマンド、CI設定変更は、そのrepoの実施計画に記録します。最初の適用計画は[wait-classificationの回帰テスト分離計画](https://github.com/bgnori/mahjong-wait-classification/blob/main/docs/lean-regression-test-cost-control-plan-2026-11-24.md)です。

## 共通方針

### テストを実行コストで階層化する

- **Fast suite:** 局所的な性質、小さい境界例、短時間で反復できる検査。通常のローカル回帰targetに含めます。
- **Exhaustive suite:** 大規模な有限列挙、組合せ探索、大きな`native_decide`評価など、編集のたびに回すには時間・メモリ負荷が高い検査。通常suiteから独立した明示targetにします。
- **Runtime integration suite:** IO、並行処理、ファイル形式など、Lean moduleのbuildだけでは実行されない`run`を持つテスト。executableを明示して起動します。

分類は行数、`native_decide`の個数、テスト名ではなく、同じ条件の実測時間と必要資源に基づけます。時間のかかる例が判明したら、宣言単位または小さなまとまり単位で測定して分類します。

### 保証を落とさず、実行経路を分ける

- テストの分割は実行配置の変更です。期待値、証明内容、入力範囲、回帰保証を理由なく削除・弱化しません。
- 通常suiteのumbrella moduleはFast suiteだけをimportします。Exhaustive suiteは独立targetとし、Fast suiteがそれを逆importしないようにします。
- CIはFast suiteと全Exhaustive suiteを明示的にbuildします。Runtime integration suiteも対応するexecutableを実行します。
- 特定suiteのみの変更で通常suiteが成功しても、そのsuiteの回帰検査を完了したとは扱いません。変更されたsuite自身のtargetを実行します。

### 計測値を比較可能にする

計測には、Lean toolchain、実行コマンド、対象target、cold/warm cache、言語サーバーの有無、CPU/worker数、メモリ上限、swap使用量を記録します。cold buildとキャッシュ済みbuildを分け、レポート生成時のruntime計測とLeanのコンパイル・証明評価時間も分けて報告します。

通常のローカルFast suiteは、代表開発環境で**おおむね60秒以内**を目標とします。超過時は、まず高コスト宣言・不要な依存・実行環境の資源圧迫を切り分け、分割または別計画での最適化を検討します。これは全マシンに対するCI失敗の固定閾値ではありません。

## 標準的な実施手順

1. 各repoでテストtarget、`native_decide`による大規模評価、IO実行ファイル、CIが実際に実行しているコマンドを棚卸しします。
2. representativeなcold/warm実行時間と、メモリ・CPU・swapなどの計測条件を記録します。
3. 高コスト検査だけをExhaustive suiteへ移し、必要なfixtureを最小限に分離します。計算本体・定理の意味・assertionは変更しません。
4. ローカルの通常コマンドがFast suiteに限定されていることを確認し、repo固有の完全回帰コマンドを文書化します。
5. CIにすべてのExhaustive targetとRuntime integration executableを明示し、全suiteを検証します。
6. 変更後に同じ条件で計測し、fast経路が短縮したことと、CIの完全検査が保たれていることを確認します。

## 完了条件

- Fast、Exhaustive、Runtime integrationの各suiteと実行方法が明確である。
- Fast suiteの依存グラフに高コスト検査が含まれず、通常のローカル反復が目標時間内に収まる。
- 全既存assertionがFastまたはExhaustive suiteのいずれかで維持され、CI上で実行される。
- IO regressionはbuild成功だけで済ませず、CIで実行結果を確認する。
- cold/warmの区別と、比較に必要な環境条件を記録する。
- repo固有の対象、コマンド、実測、例外は各repo内の実施計画から追跡できる。

## 初回適用

初回の具体的な対象・現状値・Lean module分割・workflow変更案は、[wait-classification実施計画](https://github.com/bgnori/mahjong-wait-classification/blob/main/docs/lean-regression-test-cost-control-plan-2026-11-24.md)に記録します。他repoへの適用は各repoのテスト構成を調査したうえで、個別の実施計画として追加します。
