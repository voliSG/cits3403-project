from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm
from flask_login import current_user, login_required, login_user, logout_user
from app.models import User, User_Puzzle, Puzzle
from werkzeug.urls import url_parse
from app.forms import RegistrationForm


@app.route("/")
@app.route("/index")
@login_required
def index():
    return render_template("index.html", title="Home")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/<puzzle_id>/leaderboard", methods=["GET"])
def leaderboard(puzzle_id):

    query = (
        User_Puzzle.query.filter_by(puzzle_id=puzzle_id)
        .order_by(User_Puzzle.time)
        .all()
    )

    leaderboard = [
        {"username": entry.user.username, "time": entry.time} for entry in query
    ]

    return render_template(
        "leaderboard.html",
        title="Leaderboard",
        leaderboard=leaderboard,
        puzzle_id=puzzle_id,
    )


@app.route("/user/<username>/statistics")
@login_required
def statistics(username):

    user = User.query.filter_by(username=username).first_or_404()
    query = User_Puzzle.query.filter_by(user_id=user.id).all()
    times = [puzzle.time for puzzle in query]

    average = sum(times) / len(times)
    num_puzzles = len(query)

    stats = {"username": user.username, "average": average, "num_puzzles": num_puzzles}

    return render_template("statistics.html", title="Statistics", stats=stats)


def add_puzzle(config: str) -> bool:
    if not validate_puzzle(config):
        app.logger.info("Puzzle is invalid")
    else:
        new_puzzle = Puzzle(config=config)
        db.session.add(new_puzzle)
        db.session.commit()
        app.logger.info("New puzzle succesfully added.")
        return True


def validate_puzzle(config: str) -> bool:
    pass


def submit_puzzle(puzzle_id: int, time: float, user_id: int):
    if check_puzzle():
        entry = User_Puzzle(time=time, puzzle_id=puzzle_id, user_id=user_id)
        db.session.add(entry)
        db.session.commit()


def check_puzzle() -> bool:
    return True
