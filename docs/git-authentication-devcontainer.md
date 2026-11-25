# Dev ContainerのGit認証：現状と仕組み

調査日: 2026-11-25

## 要点

GitHubへのHTTPS pushで使う認証情報は、Gitが認証ヘルパーなどから受け取る。
GitHubのPAT設定でリポジトリを対象に含めることと、GitにそのPATを渡せることは
別の条件である。VS CodeのGitHub連携やGitHub MCPが認証できることだけでは、
コンテナー内のGitが同じ認証情報を受け取れるとは限らない。

VS Code Dev Containersには、ホストのGit認証情報をコンテナー内で再利用する
仕組みがある。これはコンテナー内のGitとホストの認証ヘルパーを連携させる経路で、
コンテナー内にホストの実行ファイルや認証情報ファイルがすべてコピーされる、
という意味ではない。実際にその経路が使えるかは設定と実行環境の確認が必要である。

## 認証の経路

```text
コンテナー内の Git
  ├─ Git認証ヘルパー → gh、secret-tool、VS Codeの転送など
  └─ ヘルパーで取得できない場合 → askpass等の入力手段
                                    ↓
                       取得した認証情報でGitHubへアクセス

GitHub MCP等の連携ツール → そのツール自身の認証 → GitHub API
```

GitはURLに一致する`credential.helper`を設定順に処理する。空のhelper設定は
それまでのリストをリセットする。複数の設定がある場合、一般設定とGitHub用設定、
システム・ユーザー・リポジトリごとの設定を合わせて確認する必要がある。
`user.name`や`user.email`はコミットの作者情報であり、pushの認証情報ではない。

- **VS Code Dev Containers:** 公式資料によると、起動時にローカルの`.gitconfig`を
  コンテナーへコピーし、ホストにHTTPS用認証ヘルパーが設定されていれば、ホストと
  コンテナーで認証情報を再利用できる。ホスト側のヘルパーやVS Codeの接続状態は
  この仕組みの前提である。
- **`gh`:** GitHub CLIの`gh auth git-credential`をGit認証ヘルパーとして使う
  方式。ヘルパーが実行される環境で`gh`本体と、その`gh`が利用する認証が必要。
  ホスト上の`gh`は通常そのままコンテナー内の`/usr/bin/gh`にはならない。
- **`secret-tool`:** LinuxのSecret Serviceを利用するコマンド。Git自体の標準
  ヘルパーではないが、認証ヘルパーがSecret Serviceから値を取得してGitへ渡す
  構成にできる。実行環境のコマンド、Secret Serviceへの接続、および対象の
  認証情報が必要で、コマンドの存在だけでは動作を保証しない。
- **SSH:** HTTPSとは別の経路。Dev Containersは実行中のホストSSH agentを転送できる
  が、agentに鍵があり接続できる必要がある。現在の各`origin`はHTTPSであり、
  SSHへの変更は今回の調査対象ではない。

## この環境で確認したこと

以下は調査時点の観測であり、プロジェクトの必須設定や過去のpush手順を示すものでは
ない。ホストの設定・利用者の認証情報や、VS Codeが起動された環境は確認していない。

- workspace、Core、手牌ハッシュのローカルcloneには、一般的なVS Code Dev Containers
  の認証ヘルパーに加え、ユーザー設定のGitHub用helperに空設定と
  `/usr/bin/gh auth git-credential`がある。
- シャンテン計算のローカルGit設定には、GitHub用helperをリセットしたうえで、
  `secret-tool`から`site=github.com`に対応する値を取得し、Gitに渡す設定がある。
  これはユーザーの記憶と整合するが、過去にその経路でpushした証拠ではない。
- 待ち分類のローカルGit設定には、別の`GH_CONFIG_DIR`を指定する`gh`用helperも
  ある。上記のユーザー設定と合わせて評価されるため、設定があるだけでは実際に
  どの経路が使われたかは分からない。
- コンテナー内では`gh`と`secret-tool`が見つからず、`/usr/bin/gh`も存在しない。
  `GIT_ASKPASS`と`SSH_AUTH_SOCK`は設定されているが、設定されていることだけでは
  それらの接続や認証成功を意味しない。
- workspaceの[Dockerfile](../.devcontainer/Dockerfile)には`gh`または`secret-tool`を
  明示的にインストールする手順はない。[Dev Container設定](../.devcontainer/devcontainer.json)
  はGo featureとLean用・Mathlib用のストレージを指定している。
- 手牌ハッシュへのGit pushでは、`/usr/bin/gh`が見つからず、askpassからも認証情報を
  受け取れなかった。そのためGitHubによるPATの権限判定には至っていない。
  GitHub MCPでは当該リポジトリの情報を読み取れ、権限情報にpush可能と表示されたが、
  それはGitによるpush成功の確認ではない。
- Gitのremote-tracking reflogには他リポジトリでのpush成功が残っている。
  reflogはどのPATやhelperを使ったかを示さないため、今回の調査では過去の成功経路を
  特定できなかった。PATの対象リポジトリ一覧には手牌ハッシュも含まれているが、
  一覧だけではコンテナー内Gitへの受け渡しや必要な権限を確認できない。

## 安全な切り分けと未決定事項

1. **ホスト側の認証経路を確認する。** ホストのGitがどのhelperを使っているか、
   それが`secret-tool`、`gh`、別のcredential managerのどれに接続するかを確認する。
   必要であればVS CodeのDev Containers経由で利用できる状態か確認する。
2. **コンテナー内の設定を確認する。** `git config --show-origin --get-all
   credential.helper`と、GitHub用の`credential.https://github.com.helper`を
   リポジトリごとに確認する。空設定によるリセットとローカル設定の上書きに注意する。
   設定値に秘密が直接含まれている場合もあるため、出力を共有する前に確認する。
3. **経路を選ぶ。** ホストの認証情報をVS Code経由で共有する方法と、コンテナー内に
   `gh`またはSecret Serviceを用意する方法は別の選択肢である。後者ではインストール
   だけでなく認証情報への安全なアクセスも設計する。現時点ではどれを標準にするか、
   過去の設定を変更・削除するかは未決定である。
4. **最後にGitの動作を検証する。** 選択した経路について、認証が必要な操作を
   適切な権限・範囲で確認する。手牌ハッシュのCIを動かすには、ワークフローを含む
   コミットのpushと、GitHub Actions上でテスト不在による失敗を確認する必要がある。
   対象リポジトリの選択とは別に、ワークフロー変更に必要な権限も確認する。

PATはチャット、コマンド引数、URL、リポジトリ、ログに書かない。`git credential fill`
や`secret-tool lookup`の結果には認証情報が含まれ得るため、診断時にその出力を表示・
共有しない。確認のためだけに認証情報を別の保存先へ複製しない。

## 参考

- [VS Code: Sharing Git credentials with your container](https://code.visualstudio.com/remote/advancedcontainers/sharing-git-credentials)
- [Git: gitcredentials](https://git-scm.com/docs/gitcredentials)
