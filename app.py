from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from users import get_user, authenticate
from flask_login import UserMixin

app = Flask(__name__)
app.secret_key = "supersecretkey"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Для доступа необходимо войти"


@login_manager.user_loader
def load_user(user_id):
    return get_user(user_id)

@app.route("/")
def index():
    if "visits" in session:
        session["visits"] += 1
    else:
        session["visits"] = 1
    return render_template("index.html", visits=session["visits"])


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        remember = "remember" in request.form
        user = authenticate(username, password)
        if user:
            login_user(user, remember=remember)
            flash("Вы успешно вошли в систему.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))
        else:
            flash("Неверный логин или пароль", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("index"))


@app.route("/secret")
@login_required
def secret():
    return render_template("secret.html")

if __name__ == '__main__':
    app.run(debug=True, port=8080)