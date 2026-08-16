import os
from datetime import date, timedelta

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config
from models import Task, TaskStatus, User, db

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = "ログインしてください。"


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


def seed_default_users() -> None:
    if not User.query.filter_by(username="admin").first():
        admin_user = User(
            username="admin",
            display_name="管理者",
            password_hash=generate_password_hash("admin123"),
            role="admin",
            is_active=True,
        )
        db.session.add(admin_user)

    for username, display_name in {
        "member01": "メンバー01",
        "member02": "メンバー02",
        "member03": "メンバー03",
    }.items():
        if not User.query.filter_by(username=username).first():
            member = User(
                username=username,
                display_name=display_name,
                password_hash=generate_password_hash("password123"),
                role="member",
                is_active=True,
            )
            db.session.add(member)

    db.session.commit()


def create_or_update_user(user_id: int | None, username: str, display_name: str, role: str, password: str | None):
    if username.strip() == "" or display_name.strip() == "":
        raise ValueError("ユーザーIDと表示名は必須です。")

    if user_id:
        user = User.query.get_or_404(user_id)
        if User.query.filter(User.id != user_id, User.username == username).first():
            raise ValueError("そのユーザーIDは既に使用されています。")
        user.username = username
        user.display_name = display_name
        user.role = role
        if password:
            user.password_hash = generate_password_hash(password)
        db.session.commit()
        return user

    if User.query.filter_by(username=username).first():
        raise ValueError("そのユーザーIDは既に使用されています。")

    user = User(
        username=username,
        display_name=display_name,
        password_hash=generate_password_hash(password or "password123"),
        role=role,
    )
    db.session.add(user)
    db.session.commit()
    return user


def seed_default_tasks() -> None:
    if Task.query.count() > 0:
        return

    users = User.query.order_by(User.id.asc()).all()
    start_date = date.today()
    tasks_data = [
        {
            "task_name": "備品棚卸",
            "description": "倉庫内の備品を棚卸しして在庫を確認する",
            "due_date": start_date + timedelta(days=3),
            "priority": "high",
            "assignee_id": users[0].id,
            "statuses": {users[0].id: "done", users[1].id: "todo", users[2].id: "todo", users[3].id: "todo"},
        },
        {
            "task_name": "会議室点検",
            "description": "空調・備品・清掃状況を確認して報告する",
            "due_date": start_date + timedelta(days=7),
            "priority": "medium",
            "assignee_id": users[1].id,
            "statuses": {users[0].id: "done", users[1].id: "done", users[2].id: "todo", users[3].id: "todo"},
        },
        {
            "task_name": "来客対応資料の更新",
            "description": "来客対応の案内資料を更新する",
            "due_date": start_date + timedelta(days=10),
            "priority": "low",
            "assignee_id": users[2].id,
            "statuses": {users[0].id: "todo", users[1].id: "todo", users[2].id: "todo", users[3].id: "done"},
        },
    ]

    for item in tasks_data:
        task = Task(
            task_name=item["task_name"],
            description=item["description"],
            due_date=item["due_date"],
            priority=item["priority"],
            assignee_id=item["assignee_id"],
        )
        db.session.add(task)
        db.session.flush()

        for user_id, status in item["statuses"].items():
            db.session.add(
                TaskStatus(
                    task_id=task.id,
                    user_id=user_id,
                    status=status,
                )
            )

    db.session.commit()


def get_user_status(task: Task, user_id: int) -> str:
    status_record = TaskStatus.query.filter_by(task_id=task.id, user_id=user_id).first()
    return status_record.status if status_record else "todo"


def parse_due_date(value):
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def serialize_task(task: Task):
    return {
        "id": task.id,
        "task_name": task.task_name,
        "description": task.description,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "priority": task.priority,
        "assignee_id": task.assignee_id,
        "assignee_name": task.assignee.display_name if task.assignee else None,
        "statuses": {
            str(record.user_id): record.status for record in task.statuses
        },
    }


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()
        seed_default_users()
        seed_default_tasks()

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""

            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                if user.role == "admin":
                    return redirect(url_for("admin"))
                return redirect(url_for("index"))

            flash("ログインIDまたはパスワードが正しくありません。", "danger")

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for("login"))

    @app.route("/")
    @login_required
    def index():
        users = User.query.order_by(User.id.asc()).all()
        tasks = Task.query.order_by(Task.due_date.asc()).all()
        return render_template("index.html", tasks=tasks, users=users, current_user=current_user)

    @app.route("/tasks/<int:task_id>/status", methods=["POST"])
    @login_required
    def toggle_task_status(task_id: int):
        task = Task.query.get_or_404(task_id)
        selected_user_id = request.form.get("user_id")
        if selected_user_id is None:
            flash("更新対象のユーザーが指定されていません。", "danger")
            return redirect(url_for("index"))

        target_user_id = int(selected_user_id)
        if current_user.role != "admin" and current_user.id != target_user_id:
            flash("自分のステータスのみ更新できます。", "danger")
            return redirect(url_for("index"))

        status = TaskStatus.query.filter_by(task_id=task.id, user_id=target_user_id).first()
        if status is None:
            status = TaskStatus(task_id=task.id, user_id=target_user_id, status="done")
            db.session.add(status)
        else:
            status.status = "done" if status.status == "todo" else "todo"

        db.session.commit()
        flash("ステータスを更新しました。", "success")
        return redirect(url_for("index"))

    @app.route("/api/tasks", methods=["GET"])
    @login_required
    def api_get_tasks():
        tasks = Task.query.order_by(Task.due_date.asc()).all()
        users = User.query.order_by(User.id.asc()).all()
        return jsonify({
            "tasks": [serialize_task(task) for task in tasks],
            "users": [
                {"id": user.id, "username": user.username, "display_name": user.display_name, "role": user.role}
                for user in users
            ],
        })

    @app.route("/api/tasks", methods=["POST"])
    @login_required
    def api_create_task():
        if current_user.role != "admin":
            return jsonify({"success": False, "error": "管理者権限が必要です。"}), 403

        data = request.get_json(silent=True) or request.form
        task_name = (data.get("task_name") or "").strip()
        due_date = data.get("due_date")
        if not task_name or not due_date:
            return jsonify({"success": False, "error": "タスク名と期限は必須です。"}), 400

        task = Task(
            task_name=task_name,
            description=data.get("description") or "",
            due_date=parse_due_date(due_date),
            priority=data.get("priority") or "medium",
            assignee_id=int(data["assignee_id"]) if data.get("assignee_id") else None,
        )
        db.session.add(task)
        db.session.commit()
        return jsonify({"success": True, "task": serialize_task(task)})

    @app.route("/api/tasks/<int:task_id>", methods=["PUT"])
    @login_required
    def api_update_task(task_id: int):
        if current_user.role != "admin":
            return jsonify({"success": False, "error": "管理者権限が必要です。"}), 403

        task = Task.query.get_or_404(task_id)
        data = request.get_json(silent=True) or request.form
        task.task_name = (data.get("task_name") or task.task_name).strip()
        task.description = data.get("description") or task.description
        task.priority = data.get("priority") or task.priority
        if data.get("due_date"):
            task.due_date = parse_due_date(data.get("due_date"))
        if data.get("assignee_id"):
            task.assignee_id = int(data.get("assignee_id"))
        db.session.commit()
        return jsonify({"success": True, "task": serialize_task(task)})

    @app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
    @login_required
    def api_delete_task(task_id: int):
        if current_user.role != "admin":
            return jsonify({"success": False, "error": "管理者権限が必要です。"}), 403

        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return jsonify({"success": True, "task_id": task_id})

    @app.route("/api/status/update", methods=["POST"])
    @login_required
    def api_update_status():
        data = request.get_json(silent=True) or request.form
        task_id = data.get("task_id")
        user_id = data.get("user_id")

        if task_id is None or user_id is None:
            return jsonify({"success": False, "error": "task_id と user_id は必須です。"}), 400

        task = Task.query.get(task_id)
        if task is None:
            return jsonify({"success": False, "error": "タスクが存在しません。"}), 404

        target_user_id = int(user_id)
        if current_user.role != "admin" and current_user.id != target_user_id:
            return jsonify({"success": False, "error": "自分のステータスのみ更新できます。"}), 403

        status_record = TaskStatus.query.filter_by(task_id=task.id, user_id=target_user_id).first()
        if status_record is None:
            status_record = TaskStatus(task_id=task.id, user_id=target_user_id, status="done")
            db.session.add(status_record)
            db.session.commit()
            return jsonify({"success": True, "status": "done", "task_id": task.id, "user_id": target_user_id})

        next_status = "todo" if status_record.status == "done" else "done"
        status_record.status = next_status
        db.session.commit()
        return jsonify({"success": True, "status": next_status, "task_id": task.id, "user_id": target_user_id})

    @app.route("/admin", methods=["GET", "POST"])
    @login_required
    def admin():
        if current_user.role != "admin":
            flash("管理者権限が必要です。", "danger")
            return redirect(url_for("index"))

        editing_task = None
        if request.method == "POST":
            if "task_name" in request.form:
                task_id = request.form.get("task_id")
                task_name = (request.form.get("task_name") or "").strip()
                description = request.form.get("description") or ""
                due_date = request.form.get("due_date")
                assignee_id = request.form.get("assignee_id")
                priority = request.form.get("priority") or "medium"

                if not task_name or not due_date:
                    flash("タスク名と期限は必須です。", "danger")
                else:
                    parsed_due_date = parse_due_date(due_date)
                    if task_id:
                        task = Task.query.get_or_404(int(task_id))
                        task.task_name = task_name
                        task.description = description
                        task.due_date = parsed_due_date
                        task.priority = priority
                        task.assignee_id = int(assignee_id) if assignee_id else None
                        flash("タスクを更新しました。", "success")
                    else:
                        task = Task(
                            task_name=task_name,
                            description=description,
                            due_date=parsed_due_date,
                            priority=priority,
                            assignee_id=int(assignee_id) if assignee_id else None,
                        )
                        db.session.add(task)
                        flash("タスクを登録しました。", "success")
                    db.session.commit()

                return redirect(url_for("admin"))

        edit_id = request.args.get("edit_id")
        if edit_id:
            editing_task = Task.query.get_or_404(int(edit_id))

        tasks = Task.query.order_by(Task.due_date.asc()).all()
        users = User.query.order_by(User.id.asc()).all()
        return render_template("admin.html", tasks=tasks, users=users, editing_task=editing_task, current_user=current_user)

    @app.route("/admin/users", methods=["GET", "POST"])
    @login_required
    def admin_users():
        if current_user.role != "admin":
            flash("管理者権限が必要です。", "danger")
            return redirect(url_for("index"))

        if request.method == "POST":
            user_id = request.form.get("user_id")
            username = (request.form.get("username") or "").strip()
            display_name = (request.form.get("display_name") or "").strip()
            role = request.form.get("role") or "member"
            password = (request.form.get("password") or "").strip()

            try:
                create_or_update_user(
                    user_id=int(user_id) if user_id else None,
                    username=username,
                    display_name=display_name,
                    role=role,
                    password=password if password else None,
                )
                flash("ユーザーを保存しました。", "success")
            except ValueError as exc:
                flash(str(exc), "danger")
            return redirect(url_for("admin_users"))

        edit_user_id = request.args.get("edit_user_id")
        editing_user = User.query.get(int(edit_user_id)) if edit_user_id else None
        users = User.query.order_by(User.id.asc()).all()
        return render_template("admin_users.html", users=users, editing_user=editing_user, current_user=current_user)

    @app.route("/admin/users/<int:user_id>/delete", methods=["POST"])
    @login_required
    def delete_user(user_id: int):
        if current_user.role != "admin":
            flash("管理者権限が必要です。", "danger")
            return redirect(url_for("index"))

        if user_id == current_user.id:
            flash("自分自身は削除できません。", "danger")
            return redirect(url_for("admin_users"))

        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash("ユーザーを削除しました。", "success")
        return redirect(url_for("admin_users"))

    @app.route("/admin/tasks/<int:task_id>/delete", methods=["POST"])
    @login_required
    def delete_task(task_id: int):
        if current_user.role != "admin":
            flash("管理者権限が必要です。", "danger")
            return redirect(url_for("index"))

        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        flash("タスクを削除しました。", "success")
        return redirect(url_for("admin"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "1") == "1", host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
