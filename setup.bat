@echo off
REM タスク管理システム 完全自動セットアップスクリプト (Windows)
REM 実行: setup.bat

echo.
echo 🚀 タスク管理システム 自動セットアップ開始
echo ===========================================
echo.

REM Step 1: Python 環境確認
echo 📌 Step 1: Python 環境確認...
python --version
if errorlevel 1 (
    echo エラー: Python がインストールされていません
    echo https://www.python.org からインストールしてください
    pause
    exit /b 1
)

REM Step 2: 仮想環境作成
echo 📌 Step 2: 仮想環境作成...
python -m venv venv
call venv\Scripts\activate.bat

REM Step 3: 依存パッケージインストール
echo 📌 Step 3: 依存パッケージインストール...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo エラー: パッケージインストールに失敗しました
    pause
    exit /b 1
)

REM Step 4: .env.local 作成
echo 📌 Step 4: ローカル環境変数ファイル作成...
(
    echo SECRET_KEY=local-dev-secret-key
    echo FLASK_ENV=development
    echo FLASK_DEBUG=1
) > .env.local
echo ✅ .env.local を作成しました

REM Step 5: 完了メッセージ
echo.
echo ✅ セットアップ完了！
echo.
echo 次のステップ:
echo 1️⃣ ブラウザで http://127.0.0.1:5000 を開く
echo 2️⃣ admin / admin123 でログイン
echo 3️⃣ 管理画面が表示されることを確認
echo 4️⃣ GitHub にプッシュ
echo 5️⃣ Render で Web Service 作成
echo.
echo サーバー起動コマンド:
echo   python app.py
echo.

REM Step 6: サーバー起動（オプション）
set /p start_server=ローカルサーバーを起動しますか？ (y/n): 
if /i "%start_server%"=="y" (
    python app.py
) else (
    echo セットアップスクリプト終了
    pause
)
