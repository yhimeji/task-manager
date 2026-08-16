# Flask タスク管理システム クイックスタートガイド（メンバー向け）

**所要時間: 約 60分**

このガイドに従うだけで、Flask タスク管理システムを個人で構築・デプロイできます。

---

## 🚀 スタート前にご確認ください

### ✅ 必要な準備物

- [ ] GitHub アカウント（https://github.com）
- [ ] Render アカウント（https://render.com）
- [ ] Python 3.11 以上（https://www.python.org）
- [ ] テキストエディタ（VS Code 推奨）
- [ ] Git（https://git-scm.com）

### 📋 必要なコマンドラインスキル

- ターミナルでコマンド実行経験（cd, python, git コマンド など）

---

## 🎯 7つのステップで完成！

### **ステップ 1️⃣: プロジェクトを GitHub からクローン**

**所要時間: 2分**

ターミナルで以下を実行：

```bash
git clone https://github.com/yhimeji/task-manager.git
cd task-manager
```

✅ **確認**: `task-manager` フォルダが作成される

---

### **ステップ 2️⃣: 環境を準備**

**所要時間: 3分**

#### A. 環境変数ファイルを作成

ターミナルで以下を実行：

```bash
# .env.local ファイルを作成
echo SECRET_KEY=local-dev-secret-key > .env.local
echo FLASK_ENV=development >> .env.local
echo FLASK_DEBUG=1 >> .env.local
```

✅ **確認**: プロジェクトフォルダに `.env.local` ファイルが作成される

#### B. Python パッケージをインストール

```bash
pip install -r requirements.txt
```

✅ **確認**: インストールが完了し、エラーなし

---

### **ステップ 3️⃣: ローカル環境で起動テスト**

**所要時間: 5分**

ターミナルで以下を実行：

```bash
python app.py
```

**期待される出力:**

```
* Serving Flask app 'app'
* Debug mode: on
* Running on http://127.0.0.1:5000
```

✅ **確認**: ブラウザで http://127.0.0.1:5000 にアクセス → ログインページが表示される

#### テストログイン

- **ユーザーID**: `admin`
- **パスワード**: `admin123`

✅ **確認**: 管理画面が表示される

---

### **ステップ 4️⃣: 自分の GitHub にプッシュ**

**所要時間: 5分**

#### A. GitHub で新規リポジトリを作成

1. https://github.com/new にアクセス
2. **Repository name**: `task-manager` と入力
3. **Create repository** をクリック

#### B. コードをプッシュ

ターミナルで以下を実行（`YOUR_USERNAME` は自分の GitHub ユーザー名に置き換え）：

```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/task-manager.git
git branch -M main
git push -u origin main
```

✅ **確認**: https://github.com/YOUR_USERNAME/task-manager にコードが表示される

---

### **ステップ 5️⃣: Render で PostgreSQL を作成**

**所要時間: 10分**

#### A. Render で PostgreSQL を作成

1. https://dashboard.render.com にアクセス（GitHub でログイン）
2. **New** → **PostgreSQL** をクリック
3. 以下を入力：
   - **Name**: `task-manager-db`
   - **Database**: `taskmanager`
   - **Pricing Plan**: Free
4. **Create Database** をクリック

#### B. 接続 URL を取得

1. 作成された PostgreSQL をクリック
2. **Connections** タブを開く
3. **External Database URL** をコピー
   - 形式: `postgresql://user:password@host:5432/database`

✅ **確認**: URL がコピーできた

---

### **ステップ 6️⃣: Render で Web Service を作成・デプロイ**

**所要時間: 15分**

#### A. 新規 Web Service を作成

1. Render ダッシュボード → **+ New** → **Web Service**
2. **Connect a repository** で `task-manager` を検索・接続

#### B. 設定を入力

| 項目 | 入力値 |
|------|--------|
| **Name** | `task-manager` |
| **Environment** | `Python 3` |
| **Region** | `Singapore` など任意 |
| **Branch** | `main` |
| **Build Command** | `pip install --upgrade setuptools wheel && pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |

#### C. 環境変数を設定

以下の 4 つを追加：

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11.0` |
| `SECRET_KEY` | `あなたが生成した安全な値` ※下記参照 |
| `FLASK_ENV` | `production` |
| `DATABASE_URL` | ステップ 5 でコピーした PostgreSQL URL |

**SECRET_KEY の生成方法:**

ターミナルで以下を実行：

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

表示された値をコピーして、`SECRET_KEY` に貼り付けてください。

#### D. Web Service を作成

**Create Web Service** をクリック → 自動デプロイ開始

✅ **確認**: ステータスが 🟢 **Live** になったら成功

---

### **ステップ 7️⃣: 本番環境で確認**

**所要時間: 5分**

1. Render Web Service の URL をコピー（例: `https://task-manager-xxxxx.onrender.com`）
2. ブラウザでアクセス
3. **ユーザーID**: `admin` / **パスワード**: `admin123` でログイン
4. 管理画面が表示される

✅ **完成！** 🎉

---

## 🆘 トラブルシューティング

### ❌ ログインページが表示されない

**原因の確認:**

1. URL が正しいか確認
2. Render の **Logs** タブでエラーを確認
3. **Redeploy** をクリック

### ❌ ログインに失敗する

**確認項目:**

- ユーザーID: `admin`（スペースなし）
- パスワード: `admin123`（小文字）
- Caps Lock が OFF になっているか確認

### ❌ データベース接続エラー

**確認:**

1. Render の `DATABASE_URL` 環境変数が正しく設定されているか
2. PostgreSQL の **Status** が 🟢 Available か

---

## 📞 質問・困ったときは

1. **Render ダッシュボークの Logs タブ** でエラーメッセージを確認
2. **GitHub Issues** で類似の問題を検索
3. チーム内で共有されている FAQ を確認

---

## ✅ デプロイ完了チェックリスト

- [ ] ローカルでログイン成功
- [ ] GitHub にコード保存
- [ ] Render Web Service が Live 状態
- [ ] 本番環境でログイン成功
- [ ] 管理画面が表示される

**すべてチェックできたら、デプロイ成功です！** 🚀

---

## 📚 さらに詳しく知りたい場合

詳細な実装方法・カスタマイズ方法については、以下を参照：

**[詳細デプロイガイド](./DEPLOYMENT_GUIDE.md)** - 全 7 ステップの詳しい説明

