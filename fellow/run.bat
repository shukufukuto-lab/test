@echo off
REM Fellow 起動用バッチファイル
REM このフォルダに同梱された python-embed\python.exe を使ってアプリを起動します。
REM ユーザーのPCにPythonがインストールされている必要はありません。

cd /d "%~dp0"
python-embed\python.exe main.py

if errorlevel 1 (
    echo.
    echo ==============================
    echo  起動に失敗しました。上記のエラー内容を
    echo  情報システム部門または開発者にご連絡ください。
    echo ==============================
    pause
)
