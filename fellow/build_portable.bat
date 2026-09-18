@echo off
REM ============================================================
REM  Fellow 配布用フォルダの組み立てスクリプト(開発者用)
REM
REM  実行前に、下記URLから該当のバージョンのembeddable package(zip)を
REM  ダウンロードし、"python-embed.zip" としてこのフォルダに置いてください。
REM  https://www.python.org/downloads/windows/
REM  (例: python-3.11.9-embed-amd64.zip)
REM
REM  実行後、このフォルダをそのままZIP化してユーザーに配布できます。
REM ============================================================

cd /d "%~dp0"

if not exist python-embed.zip (
    echo python-embed.zip が見つかりません。
    echo python.org の embeddable package をダウンロードして配置してください。
    pause
    exit /b 1
)

echo [1/4] Python embeddable package を展開しています...
powershell -Command "Expand-Archive -Path python-embed.zip -DestinationPath python-embed -Force"

echo [2/4] pip を有効化しています...
REM embeddable package は標準でpipが無効なため、pth ファイルを編集して有効化
powershell -Command "(Get-Content python-embed\python*._pth) -replace '#import site', 'import site' | Set-Content python-embed\python*._pth"

echo [3/4] get-pip.py を取得し、pip をインストールしています...
powershell -Command "Invoke-WebRequest -Uri https://bootstrap.pypa.io/get-pip.py -OutFile python-embed\get-pip.py"
python-embed\python.exe python-embed\get-pip.py --no-warn-script-location

echo [4/4] 依存ライブラリをインストールしています...
python-embed\python.exe -m pip install --no-warn-script-location -r requirements.txt

echo.
echo 完了しました。フォルダ全体を配布用にZIP化してください。
pause
