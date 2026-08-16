# 社内庶務タスク管理システム

Flask ベースの社内庶務タスク管理アプリケーションです。

## 機能

- ログイン機能
- 管理者向けタスク登録・編集・削除
- メンバー向けステータス更新
- ユーザー管理
- PostgreSQL 対応
- Render へのデプロイ対応

## 必要環境

- Python 3.12+
- PostgreSQL
- Render

## セットアップ

1. 依存関係をインストール

```bash
python -m pip install -r requirements.txt
```

2. 環境変数を作成

```bash
copy .env.example .env
```

または手動で `.env` を作成し、以下を設定します。

```env
SECRET_KEY=change-this-to-a-random-secret-key
DATABASE_URL=postgresql://username:password@host:port/database_name
FLASK_ENV=production
```

3. アプリを起動

```bash
python app.py
```

ローカル開発時は `http://127.0.0.1:5000/login` でアクセスできます。

## Render デプロイ

1. GitHub リポジトリを Render に接続
2. `main` ブランチを選択
3. Web Service を作成
4. Build Command

```bash
pip install -r requirements.txt
```

5. Start Command

```bash
gunicorn app:app
```

6. 環境変数として `SECRET_KEY` と `DATABASE_URL` を登録

## 初期ユーザー

- admin / admin123
- member01 / password123
- member02 / password123
- member03 / password123

## 重要

- `.env` は Git 管理対象外です。
- 本番環境では `SECRET_KEY` を必ず変更してください。
