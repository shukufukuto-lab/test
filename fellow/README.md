# Fellow - 工数管理アプリ(プロトタイプ)

案件×要員×月の計画工数と、タイマー/手動入力による実績工数を管理するFletアプリ。

## セットアップ

```bash
pip install -r requirements.txt
python main.py
```

## 画面構成

- ホーム: タイマーで稼働時間を計測
- 手動入力: 後から時間帯を指定して記録を追加・編集
- 集計・ダッシュボード: 案件別の計画 vs 実績を表示
- 案件マスタ / 要員マスタ / 計画工数登録: マスタデータの管理

## データ

初回起動時に `fellow.db` (SQLite) が自動生成され、サンプルの案件・要員が投入されます。

## 配布方法(Python未インストール端末向け・exe化なし)

社内のセキュリティポリシーで未署名exeが実行できない場合、Pythonの
「embeddable package(展開版)」をアプリと同じフォルダに同梱し、
`.bat`ファイルから起動する方式を使う。

1. 開発者のWindows機で、[python.org](https://www.python.org/downloads/windows/) から
   使用中のPythonバージョンに合う「Windows embeddable package (64-bit)」の
   zipをダウンロードし、このフォルダに `python-embed.zip` として置く
2. `build_portable.bat` を実行する
   (Python本体の展開・pip有効化・`requirements.txt`のインストールまで自動で行う)
3. 完成した `fellow` フォルダ全体をZIP化してユーザーに配布する

### ユーザー側の使い方

1. 配布されたZIPを展開する
2. `run.bat` をダブルクリックする(インストール操作は不要)

この方式なら、実行されるのはPython公式配布の`python.exe`であり、
未署名の独自exeではないため、SmartScreenの警告やブロックの対象になりにくい。
ただし、配布フォルダのサイズは大きくなる(Python本体+ライブラリ+Flutter描画エンジン分)。

## 未実装(次のステップ)

- ウィンドウタイトルからの案件自動推測
- Excelマスタからの初回取込
- チーム共有(サーバー連携)
- ログインユーザーに応じた `staff_id` の切替(現在は田中で固定)
