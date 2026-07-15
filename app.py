"""
AI Agent Certification Lab
===========================
A full-stack Flask application that teaches and certifies users on
building AI agents through hands-on, auto-graded modules and a final
certification exam that issues a downloadable PDF certificate.

Run:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000
"""

import os
import uuid
import random
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()  # loads variables from a local .env file, if present

from flask import (
    Flask, render_template, redirect, url_for, request,
    flash, session, send_from_directory, abort
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

from certificate import generate_certificate
from lab_content import MODULES, FINAL_EXAM

# ---------------------------------------------------------------------------
# App / Config
# ---------------------------------------------------------------------------
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

# Use DATABASE_URL if provided (e.g. Postgres on Render/Railway/Fly), else fall
# back to a local SQLite file for simple/demo deployments.
database_url = os.environ.get("DATABASE_URL", "")
if database_url.startswith("postgres://"):
    # SQLAlchemy 1.4+ requires the "postgresql://" scheme, not "postgres://"
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or (
    "sqlite:///" + os.path.join(basedir, "instance", "lab.db")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["CERT_FOLDER"] = os.environ.get(
    "CERT_FOLDER", os.path.join(basedir, "certificates")
)

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    progress = db.relationship("ModuleProgress", backref="user", lazy=True)
    certificate = db.relationship("Certificate", backref="user", uselist=False)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def completed_module_ids(self):
        return {p.module_id for p in self.progress if p.completed}

    def all_modules_complete(self):
        return len(self.completed_module_ids()) >= len(MODULES)


class ModuleProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    module_id = db.Column(db.String(50), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)
    attempts = db.Column(db.Integer, default=0)
    completed_at = db.Column(db.DateTime)

    __table_args__ = (db.UniqueConstraint("user_id", "module_id", name="uq_user_module"),)


class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    cert_id = db.Column(db.String(36), unique=True, nullable=False)
    final_score = db.Column(db.Integer, nullable=False)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    filename = db.Column(db.String(255), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not full_name or not email or not password:
            flash("Please fill in all fields.", "danger")
        elif len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
        elif password != confirm:
            flash("Passwords do not match.", "danger")
        elif User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "danger")
        else:
            user = User(full_name=full_name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            for module in MODULES:
                db.session.add(ModuleProgress(user_id=user.id, module_id=module["id"]))
            db.session.commit()

            login_user(user)
            flash("Account created! Welcome to the AI Agent Certification Lab.", "success")
            return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f"Welcome back, {user.full_name.split(' ')[0]}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))
        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Dashboard & modules
# ---------------------------------------------------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    completed_ids = current_user.completed_module_ids()
    progress_map = {p.module_id: p for p in current_user.progress}

    modules_view = []
    for m in MODULES:
        p = progress_map.get(m["id"])
        modules_view.append({
            "id": m["id"],
            "title": m["title"],
            "summary": m["summary"],
            "difficulty": m["difficulty"],
            "completed": p.completed if p else False,
            "score": p.score if p else 0,
            "attempts": p.attempts if p else 0,
        })

    total = len(MODULES)
    done = len(completed_ids)
    percent = int((done / total) * 100) if total else 0

    return render_template(
        "dashboard.html",
        modules=modules_view,
        percent=percent,
        done=done,
        total=total,
        all_complete=current_user.all_modules_complete(),
        certificate=current_user.certificate,
    )


@app.route("/module/<module_id>", methods=["GET", "POST"])
@login_required
def module_view(module_id):
    module = next((m for m in MODULES if m["id"] == module_id), None)
    if module is None:
        abort(404)

    progress = ModuleProgress.query.filter_by(
        user_id=current_user.id, module_id=module_id
    ).first()
    if progress is None:
        progress = ModuleProgress(user_id=current_user.id, module_id=module_id)
        db.session.add(progress)
        db.session.commit()

    result = None

    if request.method == "POST":
        progress.attempts = (progress.attempts or 0) + 1
        answers = {}
        correct = 0
        for i, q in enumerate(module["quiz"]):
            key = f"q{i}"
            submitted = request.form.get(key)
            answers[key] = submitted
            if submitted is not None and int(submitted) == q["answer_index"]:
                correct += 1

        score = int((correct / len(module["quiz"])) * 100)
        passed = score >= module["pass_score"]

        progress.score = max(progress.score or 0, score)
        if passed:
            progress.completed = True
            progress.completed_at = datetime.utcnow()
        db.session.commit()

        result = {
            "score": score,
            "correct": correct,
            "total": len(module["quiz"]),
            "passed": passed,
            "pass_score": module["pass_score"],
        }

    return render_template("module.html", module=module, progress=progress, result=result)


# ---------------------------------------------------------------------------
# Final certification exam
# ---------------------------------------------------------------------------
@app.route("/exam", methods=["GET", "POST"])
@login_required
def exam():
    if not current_user.all_modules_complete():
        flash("Complete all modules before attempting the certification exam.", "warning")
        return redirect(url_for("dashboard"))

    if current_user.certificate:
        return redirect(url_for("view_certificate"))

    result = None

    if request.method == "POST":
        correct = 0
        for i, q in enumerate(FINAL_EXAM):
            submitted = request.form.get(f"q{i}")
            if submitted is not None and int(submitted) == q["answer_index"]:
                correct += 1

        score = int((correct / len(FINAL_EXAM)) * 100)
        passed = score >= 80

        result = {"score": score, "correct": correct, "total": len(FINAL_EXAM), "passed": passed}

        if passed:
            cert_id = str(uuid.uuid4())
            filename = f"certificate_{current_user.id}_{cert_id[:8]}.pdf"
            filepath = os.path.join(app.config["CERT_FOLDER"], filename)

            generate_certificate(
                filepath=filepath,
                full_name=current_user.full_name,
                cert_id=cert_id,
                score=score,
                issue_date=datetime.utcnow(),
            )

            cert = Certificate(
                user_id=current_user.id,
                cert_id=cert_id,
                final_score=score,
                filename=filename,
            )
            db.session.add(cert)
            db.session.commit()

            flash("Congratulations! You passed and earned your certificate.", "success")
            return redirect(url_for("view_certificate"))

    return render_template("exam.html", questions=FINAL_EXAM, result=result)


@app.route("/certificate")
@login_required
def view_certificate():
    if not current_user.certificate:
        return redirect(url_for("dashboard"))
    return render_template("certificate.html", certificate=current_user.certificate, user=current_user)


@app.route("/certificate/download")
@login_required
def download_certificate():
    if not current_user.certificate:
        abort(404)
    return send_from_directory(
        app.config["CERT_FOLDER"],
        current_user.certificate.filename,
        as_attachment=True,
        download_name=f"AI_Agent_Certification_{current_user.full_name.replace(' ', '_')}.pdf",
    )


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
def init_db():
    os.makedirs(os.path.join(basedir, "instance"), exist_ok=True)
    os.makedirs(app.config["CERT_FOLDER"], exist_ok=True)
    with app.app_context():
        db.create_all()


# Initialize the database/certificate folder as soon as the app module is
# imported. This matters in production, where a WSGI server like gunicorn
# imports `app:app` directly and never runs the `if __name__ == "__main__"`
# block below.
init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
