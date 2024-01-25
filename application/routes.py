from application import app
from application import db
from application import login_manager
from application import bcrypt
from application.models import User
from application.models import History
from application.models import Worker
from application.forms import SignUpForm, SignInForm, ChangePasswordForm
from datetime import datetime
from flask_login import UserMixin, login_user, login_required, current_user, logout_user
from flask import render_template, request, flash, url_for, redirect, jsonify
from wtforms.validators import (
    Length,
    InputRequired,
    ValidationError,
    NumberRange,
    DataRequired,
    EqualTo,
    Email,
    Length,
    Optional,
)


# Handles http://127.0.0.1:5000/test
@app.route("/test")
def test():
    return "<h1>server is up!</h1>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Handles http://127.0.0.1:5000/signin
@app.route("/", methods=["GET", "POST"])
@app.route("/signin", methods=["GET", "POST"])
def signin():
    form = SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect("/home")
            else:
                flash("Password is incorrect")
        else:
            flash("Email is not found")
    return render_template("signin.html", title="Sign In", form=form)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already in use.\nPlease sign in or use another email.")
            return render_template("signup.html", form=form)

        hashed_password = bcrypt.generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        try:
            db.session.commit()
        except Exception as e:
            flash(f"An error occurred: {e}")
            return render_template("signup.html", form=form)

        flash("Account created successfully!\nPlease sign in.")
        return redirect(url_for("signin"))

    return render_template("signup.html", form=form)


@app.route("/home", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def index_page():
    try:
        email = current_user.email
    except Exception as e:
        print(e)
        data = request.get_json()
        email = data["email"]
        try:
            db.session.commit()
        except Exception as e:
            flash(f"An error occurred: {e}")
            return render_template("index.html", title="Home", user_email=email)
    return render_template("index.html", title="Home", user_email=email)


def get_label(form, field):
    field_data = getattr(form, field).data
    return next(
        (label for value, label in getattr(form, field).choices if value == field_data),
        None,
    )


def add_entry(new_entry):
    try:
        db.session.add(new_entry)
        db.session.commit()
        return new_entry.id
    except Exception as error:
        db.session.rollback()
        flash(error, "danger")


@app.route("/history")
@login_required
def history_page():
    try:
        entries = get_entries()
        return render_template("history.html", title="History", entries=entries)
    except Exception as e:
        flash(f"An error occurred: {e}")
        return render_template("index.html")


def get_entries():
    try:
        entries = (
            db.session.query(
                History.entry_id,
                Worker.name,
                History.temperature,
                History.creation_time,
            )
            .outerjoin(Worker, Worker.id == History.worker_id)
            .order_by(History.entry_id.desc())
            .all()
        )

        formatted_entries = []
        for entry in entries:
            formatted_entries.append(
                {
                    "id": entry.entry_id,
                    "name": entry.name if entry.name else "unknown",
                    "temperature": entry.temperature,
                    "creation_time": entry.creation_time,
                }
            )

        return formatted_entries
    except Exception as e:
        flash(f"An error occurred: {e}")
        return []


@app.route("/remove", methods=["POST"])
def remove():
    req = request.form
    id = req["id"]
    remove_entry(id)
    return redirect("/history")


def remove_entry(id):
    try:
        entry = db.get_or_404(History, id)
        db.session.delete(entry)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        flash(error, "danger")
        return 0


@app.route("/account", methods=["GET", "POST"])
def account_page():
    try:
        email = current_user.email
    except Exception as e:
        print(e)
        data = request.get_json()
        email = data["email"]
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = get_user(email)

        # Check for current password correctness
        if user and bcrypt.check_password_hash(
            user.password, form.current_password.data
        ):
            # Change password if 'Change Password' button is clicked
            if form.submit_change.data:
                user.password = bcrypt.generate_password_hash(form.new_password.data)
                db.session.commit()
                flash("Password changed successfully.")
            # Delete account if 'Delete Account' button is clicked
            elif form.submit_delete.data:
                db.session.delete(user)
                db.session.commit()
                flash("Account deleted.")
        else:
            flash("Incorrect current password.")
        return redirect("/signin")

    return render_template(
        "account.html",
        title="Account",
        user_email=email,
        form=form,
        index=True,
    )


def get_user(email):
    try:
        user = (
            db.session.execute(db.select(User).where(User.email == email))
            .scalars()
            .first()
        )
        return user
    except Exception as e:
        flash(f"An error occurred: {e}")
        return None


# ====================================================================================
# ====================================================================================
# ====================================================================================
@app.route("/api/signin", methods=["GET", "POST"])
def api_signin():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        return jsonify({"status": "success", "message": "Logged in successfully"}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401


@app.route("/api/signup", methods=["GET", "POST"])
def api_signup(data=None):
    if data is None:
        data = request.get_json()
        email = data["email"]
        password = data["password"]
        print(data)
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"status": "error", "message": "Email already in use"}), 400

        hashed_password = bcrypt.generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        try:
            db.session.commit()
            return (
                jsonify(
                    {"status": "success", "message": "Account created successfully"}
                ),
                201,
            )
        except Exception:
            return jsonify({"status": "error", "message": "Server Error"}), 500
    return jsonify({"status": "error", "message": "Invalid data"}), 400


@app.route("/api/delete_account", methods=["POST"])
def api_delete_account(data=None):
    if data is None:
        data = request.get_json()
    user_email = data["email"]
    user = User.query.filter_by(email=user_email).first()

    if user:
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        return (
            jsonify({"status": "success", "message": "Account deleted successfully"}),
            200,
        )
    else:
        return jsonify({"status": "error", "message": "User not found"}), 404


@app.route("/api/add", methods=["POST"])
def add_worker_entry():
    if request.method == "POST":
        try:
            data = request.json
            worker_id = data.get("worker_id")
            temperature = data.get("temperature")

            # Validating if both parameters are provided
            if worker_id is None or temperature is None:
                return jsonify({"error": "Missing worker_id or temperature"}), 400

            # Create a new History record (no need to check if worker exists)
            new_history = History(worker_id=worker_id, temperature=temperature)
            db.session.add(new_history)
            db.session.commit()

            return jsonify({"message": "History record added successfully"}), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/api/add_worker", methods=["POST"])
def add_worker():
    try:
        data = request.json
        worker_id = data.get("worker_id")
        name = data.get("name")

        if not all([worker_id, name]):
            return jsonify({"error": "Missing worker_id or name"}), 400

        existing_worker = Worker.query.filter_by(id=worker_id).first()
        if existing_worker:
            return jsonify({"error": "Worker with this ID already exists"}), 409

        new_worker = Worker(id=worker_id, name=name)
        db.session.add(new_worker)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "New worker added successfully",
                    "worker_id": worker_id,
                    "name": name,
                }
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/delete_worker/<int:worker_id>", methods=["DELETE"])
def delete_worker(worker_id):
    try:
        worker = Worker.query.get(worker_id)
        if not worker:
            return jsonify({"error": "Worker not found"}), 404

        db.session.delete(worker)
        db.session.commit()

        return jsonify({"message": "Worker deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
