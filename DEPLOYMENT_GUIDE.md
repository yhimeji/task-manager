# Flask タスク管理システム 完全デプロイガイド

このガイドは、「社内庶務タスク管理システム」を構築し、Render にデプロイするまでの完全な手順です。

---

## 📋 全体ステップ概要

| # | ステップ | 内容 | 所要時間 |
|---|---------|------|--------|
| 0️⃣ | **プロジェクト初期化** | Flask アプリケーション骨組み作成 | 5-10分 |
| 1️⃣ | **環境設定確認** | .env ファイル作成・設定 | 5分 |
| 2️⃣ | **PostgreSQL 設定** | Render PostgreSQL 作成・接続 URL 取得 | 10分 |
| 3️⃣ | **ローカル起動テスト** | Flask 開発サーバーでの動作確認 | 5分 |
| 4️⃣ | **エラーハンドリング** | エラーページ・ハンドラー追加 | 10分 |
| 5️⃣ | **ログイン強化** | 詳細なエラーメッセージ実装 | 5分 |
| 6️⃣ | **GitHub へプッシュ** | コードをリポジトリに保存 | 5分 |
| 7️⃣ | **Render デプロイ** | Web Service 作成・デプロイ実行 | 10分 |

**合計所要時間: 約 55-60分**

---

## ✅ ステップ 0: プロジェクト初期化

### 📁 プロジェクト構造

```
task-manager/
├── app.py                 # Flask メインアプリケーション
├── config.py              # 環境設定
├── models.py              # SQLAlchemy モデル定義
├── requirements.txt       # Python 依存パッケージ
├── .gitignore             # Git 除外設定
├── .env.example           # 環境変数テンプレート
├── .env.local             # ローカル開発用環境変数
├── README.md              # プロジェクト説明書
└── templates/
    ├── login.html         # ログインページ
    ├── index.html         # タスク一覧ページ（メンバー用）
    ├── admin.html         # タスク管理ページ（管理者用）
    ├── admin_users.html   # ユーザー管理ページ（管理者用）
    └── error.html         # エラーページ
```

### 🔧 主要ファイルの説明

| ファイル | 説明 |
|---------|------|
| **app.py** | Flask アプリケーションのメインファイル。すべてのルート・API・ビジネスロジック含む |
| **models.py** | SQLAlchemy ORM モデル。User・Task・TaskStatus テーブル定義 |
| **config.py** | 環境変数から設定を読み込む。FLASK_ENV・DATABASE_URL・SECRET_KEY など |
| **requirements.txt** | pip でインストールするパッケージ一覧 |

### 📝 依存パッケージ（requirements.txt）

```
Flask==3.0.3
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
psycopg2-binary==2.9.9
gunicorn==22.0.0
python-dotenv==1.0.1
```

---

## ✅ ステップ 1: 環境設定確認

### 📌 ローカル開発環境用 (.env.local)

**目的**: ローカルでの開発時に SQLite を使用するための設定

**内容:**
```
SECRET_KEY=local-dev-secret-key
FLASK_ENV=development
FLASK_DEBUG=1
```

**確認方法:**
```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv('.env.local'); print(os.getenv('FLASK_ENV'))"
```

**期待結果:** `development` と表示される

---

## ✅ ステップ 2: PostgreSQL 設定

### 🗄️ Render PostgreSQL の準備

**A. Render ダッシュボードでデータベース作成**

1. https://dashboard.render.com にアクセス
2. **「New」** → **「PostgreSQL」** をクリック
3. 以下を設定：
   - **Name**: `task-manager-db` (または任意の名前)
   - **Database**: `taskmanager`
   - **Pricing Plan**: `Free`
4. **「Create Database」** をクリック

**B. 接続 URL の取得**

1. 作成した PostgreSQL をクリック
2. **「Connections」** タブを開く
3. **「External Database URL」** をコピー
   - 形式: `postgresql://user:password@host:5432/database`

**重要**: この URL は後で `DATABASE_URL` 環境変数として設定します。

---

## ✅ ステップ 3: ローカル起動テスト

### 🚀 Flask 開発サーバーの起動

**コマンド:**
```bash
cd task-manager
python app.py
```

**期待結果:**
```
* Serving Flask app 'app'
* Debug mode: on
* Running on http://127.0.0.1:5000
* Debugger PIN: XXXXXX
```

### 🧪 動作確認

**ブラウザでアクセス:**
```
http://127.0.0.1:5000/login
```

**期待される動作:**
- ✅ ログインページが表示される
- ✅ ユーザーID とパスワード入力欄が見える

### 📝 初期ユーザー情報

| ユーザー | パスワード | 役割 |
|---------|----------|------|
| `admin` | `admin123` | 管理者 |
| `member01` | `password123` | メンバー |
| `member02` | `password123` | メンバー |
| `member03` | `password123` | メンバー |

**テスト方法:**
1. ユーザーID: `admin`、パスワード: `admin123` でログイン
2. 管理画面 (`/admin`) にリダイレクトされる
3. タスク・ユーザー管理画面が表示される

---

## ✅ ステップ 4: エラーハンドリング強化

### 🛡️ 実装内容

**1. エラーハンドラの追加 (app.py)**

```python
@app.errorhandler(400)
def bad_request(error):
    return render_template("error.html", code=400, message="不正なリクエストです。"), 400

@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", code=404, message="ページが見つかりません。"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("error.html", code=500, message="サーバーエラーが発生しました。"), 500
```

**2. エラーページテンプレート (templates/error.html)**

- エラーコード（400・404・500）を表示
- エラーメッセージを日本語で表示
- ホームに戻るボタンを提供

**3. DB 操作の例外処理**

主要な DB 操作 (INSERT・UPDATE・DELETE) に `try-except` を追加：

```python
try:
    # DB操作
    db.session.commit()
except Exception as exc:
    db.session.rollback()
    flash("操作に失敗しました。", "danger")
```

### 🧪 テスト方法

1. **404 エラー確認**: `http://127.0.0.1:5000/nonexistent` にアクセス
   - エラーページが表示される

2. **ログイン失敗メッセージ確認**: `/login` で
   - 存在しないユーザー → 「そのユーザーIDは存在しません。」
   - 間違ったパスワード → 「パスワードが正しくありません。」

---

## ✅ ステップ 5: ログイン強化

### 📝 実装内容

**ログイン失敗メッセージの詳細化 (app.py)**

```python
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        if not username:
            flash("ユーザーIDを入力してください。", "danger")
            return render_template("login.html")

        user = User.query.filter_by(username=username).first()
        if user is None:
            flash("そのユーザーIDは存在しません。", "danger")
            return render_template("login.html")

        if not check_password_hash(user.password_hash, password):
            flash("パスワードが正しくありません。", "danger")
            return render_template("login.html")

        # ログイン成功時の処理
        login_user(user)
        if user.role == "admin":
            return redirect(url_for("admin"))
        return redirect(url_for("index"))

    return render_template("login.html")
```

### 🧪 テスト方法

| テストケース | 期待される結果 |
|-------------|---------------|
| ユーザーID なし | 「ユーザーIDを入力してください。」 |
| ユーザーID 存在しない | 「そのユーザーIDは存在しません。」 |
| パスワード 間違い | 「パスワードが正しくありません。」 |
| 正しい認証情報 | ログイン成功 → 管理画面/タスク一覧 |

---

## ✅ ステップ 6: GitHub へプッシュ

### 🔑 Git 初期化・コミット

**1. Git を初期化（初回のみ）**
```bash
git init
git config user.email "your-email@example.com"
git config user.name "Your Name"
```

**2. GitHub リポジトリを作成**

- https://github.com/new にアクセス
- リポジトリ名: `task-manager`
- 「Create repository」をクリック

**3. コードをプッシュ**

```bash
git add .
git commit -m "Initial commit: Task management system"
git remote add origin https://github.com/YOUR_USERNAME/task-manager.git
git branch -M main
git push -u origin main
```

**確認:**
- GitHub で https://github.com/YOUR_USERNAME/task-manager を開く
- ファイルが表示される

---

## ✅ ステップ 7: Render デプロイ

### 🚀 Render Web Service 作成

**A. 新規 Web Service を作成**

1. Render ダッシュボード → **「+ New」** → **「Web Service」**
2. GitHub で `task-manager` リポジトリを選択・接続

**B. Web Service 設定**

| 項目 | 値 |
|------|-----|
| **Name** | `task-manager` |
| **Environment** | `Python 3` |
| **Region** | `Singapore` など任意 |
| **Branch** | `main` |
| **Build Command** | `pip install --upgrade setuptools wheel && pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Pricing Plan** | `Free` |

**C. 環境変数を設定**

以下 3 つを **Environment Variables** に追加：

| Key | Value |
|-----|-------|
| `SECRET_KEY` | 生成された安全な値（例: `51f5c60e3fe14675c6c45ffcf849f63cde6031e1216fd16b7242a473ee5e6bbe`） |
| `FLASK_ENV` | `production` |
| `DATABASE_URL` | ステップ 2 で取得した PostgreSQL 接続 URL |

**重要な設定:**

```
PYTHON_VERSION=3.11.0
```

Linux 環境での psycopg2 コンパイルエラー対策。

**D. デプロイ実行**

**「Create Web Service」** をクリック → 自動デプロイ開始

### 📊 デプロイ状況確認

**Logs タブで以下を監視:**

```
🔵 Building...
   → pip install setuptools wheel
   → pip install -r requirements.txt
🟡 Deploying...
   → gunicorn app:app 起動
🟢 Live
   → Your service is live
```

### ✅ デプロイ完了確認

1. **ステータスが 🟢 Green になったか確認**
2. **表示された URL をブラウザで開く**
   ```
   https://task-manager-xxxxx.onrender.com
   ```
3. **ログインページが表示されるか確認**
4. **初期ユーザーでログイン試行**

---

## 📝 トラブルシューティング

### ❌ デプロイが失敗した場合

**1. Logs タブでエラーを確認**
- `ModuleNotFoundError` → requirements.txt を確認
- `psycopg2 error` → PYTHON_VERSION を 3.11.0 に設定・再デプロイ
- `DATABASE_URL not found` → 環境変数が正しく設定されているか確認

**2. 再デプロイ**

Render ダッシュボード → **task-manager** → **Menu** → **Redeploy**

### ❌ ログインできない場合

1. データベースが正しく作成されているか確認
2. `admin` / `admin123` の認証情報が正しいか確認
3. 本番環境のログ確認: Render **Logs** タブ

### ❌ スタイルシートが適用されない場合

`Flask` キャッシュをクリア。ブラウザの開発者ツール → **Network** → **Disable cache** を有効にしてテスト。

---

## 🎯 デプロイ後の検証チェックリスト

- [ ] ログインページが表示される
- [ ] `admin` / `admin123` でログイン成功
- [ ] 管理画面（/admin）が表示される
- [ ] タスク一覧（/）が表示される
- [ ] メンバーでログイン可能
- [ ] タスク作成・編集・削除が可能
- [ ] ステータス更新（Ajax）が動作
- [ ] エラーページが正常に表示される

---

## 📚 主要ファイル概要

### app.py（~500 行）

**主な機能:**
- Flask アプリケーション初期化
- ログイン・ロジア登録
- タスク CRUD 操作
- ユーザー管理
- REST API エンドポイント
- エラーハンドラー
- 初期データシード

**重要な関数:**
- `create_app()` - アプリケーションファクトリー
- `seed_default_users()` - 初期ユーザー作成
- `seed_default_tasks()` - サンプルタスク作成
- `parse_due_date()` - 日付文字列を date オブジェクトに変換
- `serialize_task()` - Task を JSON に変換

### models.py（~65 行）

**定義されるテーブル:**
- **User**: id, username, display_name, password_hash, role, is_active, created_at, updated_at
- **Task**: id, task_name, description, due_date, priority, assignee_id, created_at, updated_at
- **TaskStatus**: id, task_id, user_id, status, created_at, updated_at

### templates/（5 つの HTML ファイル）

| ファイル | 用途 |
|---------|------|
| **login.html** | ログイン画面 |
| **index.html** | タスク一覧（メンバー用・読み取り専用） |
| **admin.html** | タスク管理（管理者用） |
| **admin_users.html** | ユーザー管理（管理者用） |
| **error.html** | エラー表示ページ |

---

## 🔐 初期認証情報

| ユーザー | パスワード | 役割 | 用途 |
|---------|----------|------|------|
| `admin` | `admin123` | 管理者 | タスク・ユーザー管理 |
| `member01` | `password123` | メンバー | タスク確認・ステータス更新 |
| `member02` | `password123` | メンバー | タスク確認・ステータス更新 |
| `member03` | `password123` | メンバー | タスク確認・ステータス更新 |

---

## 📞 サポート情報

**よくある質問:**

**Q. 本番環境でデータベースが初期化される？**
- A. いいえ。`db.create_all()` は存在しないテーブルのみ作成します。データは保持されます。

**Q. 無料プランの制限は？**
- A. 月間 550 時間の制限あり。常時稼働で月 30 日 × 24 時間 = 720 時間のため、無料プランでは運用不可。

**Q. SECRET_KEY は定期的に変更すべき？**
- A. 推奨。セッションを無効にしたい場合は変更してください。

---

**このガイドに従えば、完全な Flask タスク管理システムを Render にデプロイできます！** 🚀
