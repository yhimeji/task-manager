#!/bin/bash

# タスク管理システム 完全自動セットアップスクリプト
# 実行: bash setup.sh

set -e  # エラーで停止

echo "🚀 タスク管理システム 自動セットアップ開始"
echo "==========================================="

# Step 1: Python 環境確認
echo "📌 Step 1: Python 環境確認..."
python --version
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Step 2: 依存パッケージインストール
echo "📌 Step 2: 依存パッケージインストール..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 3: .env.local 作成
echo "📌 Step 3: ローカル環境変数ファイル作成..."
cat > .env.local << EOF
SECRET_KEY=local-dev-secret-key
FLASK_ENV=development
FLASK_DEBUG=1
EOF
echo "✅ .env.local を作成しました"

# Step 4: ローカル起動テスト
echo "📌 Step 4: ローカル起動テスト..."
echo "ブラウザで http://127.0.0.1:5000 にアクセスしてください"
echo "テストログイン: admin / admin123"
echo ""
echo "✅ セットアップ完了！"
echo ""
echo "次のステップ:"
echo "1️⃣ ブラウザでログインページを確認"
echo "2️⃣ admin/admin123 でログイン試行"
echo "3️⃣ GitHub にプッシュ"
echo "4️⃣ Render で Web Service 作成"
echo ""
echo "続ける場合は、Ctrl+C で終了後、別ターミナルで以下を実行："
echo "python app.py"
echo ""

# Step 5: Flask 開発サーバー起動（オプション）
read -p "ローカルサーバーを起動しますか？ (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python app.py
fi
