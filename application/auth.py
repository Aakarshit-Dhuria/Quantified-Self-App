from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from .database import db
from .views import *

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        user = User.query.filter_by(name=name).first()
        if user:
            if password == user.password:
                login_user(user, remember=True)
                return redirect(url_for("views.index"))
            else:
                login_user(user, remember=True)
                return redirect(url_for("views.index"))
        else:
            new_user = User(name=name, password=password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for("views.index"))


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out from the application", category="success")
    return redirect(url_for("auth.login"))
