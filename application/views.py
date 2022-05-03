from sqlite3 import Timestamp
from flask import Blueprint, Flask, redirect, request, url_for, flash
from flask import render_template
from flask import current_app as app
from .models import User, Tracker, Log
from .database import db
from flask_login import current_user, login_required, login_user
import datetime
import matplotlib.pyplot as plt
import os

views = Blueprint("views", __name__)


@views.route("/", methods=["GET", "POST"])
@login_required
def index():
    print(current_user)
    tracker = Tracker.query.all()
    return render_template("tracker_home.html", user=current_user, trackers=tracker)


@views.route("/add-tracker", methods=["GET", "POST"])
@login_required
def add_tracker():
    if request.method == "GET":
        return render_template("add_tracker.html", user=current_user)
    elif request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        tracker_type = request.form.get("type")
        settings = request.form.get("settings")
        current_user_id = current_user.id
        tracker = Tracker.query.filter_by(name=name).first()
        if tracker and current_user_id == tracker.user_id:
            flash(
                'The tracker "' + name + '" is already added by you.', category="error"
            )
            return redirect(url_for("views.index"))
        else:
            new_tracker = Tracker(
                name=name,
                description=description,
                tracker_type=tracker_type,
                setting=settings,
                user_id=current_user_id,
            )
            db.session.add(new_tracker)
            db.session.commit()
            flash("New tracker successfully added.", category="success")
            return redirect(url_for("views.index"))


@views.route("/edit-tracker/<int:record_id>", methods=["GET", "POST"])
@login_required
def edit_tracker(record_id):
    from .models import Tracker

    this_tracker = Tracker.query.get(record_id)
    this_tracker_name = this_tracker.name
    try:
        if request.method == "POST":
            name = request.form.get("name")
            description = request.form.get("description")
            tracker_type = this_tracker.tracker_type
            settings = request.form.get("settings")

            current_user_id = current_user.id
            tracker = Tracker.query.filter_by(name=name).first()
            if (
                tracker
                and tracker.user_id == current_user_id
                and this_tracker_name != name
            ):
                flash(
                    'The tracker "'
                    + name
                    + '" is already added by you, Try a new name for your tracker.',
                    category="error",
                )
            else:
                from . import db

                this_tracker.name = name
                this_tracker.description = description
                this_tracker.tracker_type = tracker_type
                this_tracker.setting = settings
                db.session.commit()
                flash("Tracker Updated Successfully.", category="success")
                return redirect(url_for("views.index"))
    except Exception as e:
        print(e)
        flash("Something went wrong.", category="error")
    return render_template("edit_tracker.html", user=current_user, tracker=this_tracker)


@views.route("/delete-tracker/<int:record_id>", methods=["GET", "POST"])
@login_required
def delete_tracker(record_id):
    try:
        Tracker_details = Tracker.query.get(record_id)
        Tracker_name = Tracker_details.name
        db.session.delete(Tracker_details)
        db.session.commit()
        flash(Tracker_name + " Tracker Removed Successfully.", category="success")
    except Exception as e:
        print(e)
        flash("Something went wrong.", category="error")
    return redirect(url_for("views.index"))


@views.route("/add-log/<int:record_id>", methods=["GET", "POST"])
@login_required
def add_log(record_id):
    this_tracker = Tracker.query.get(record_id)
    from datetime import datetime

    now = datetime.now()
    try:
        if request.method == "POST":
            when = request.form.get("date")
            value = request.form.get("value")
            notes = request.form.get("notes")

            new_log = Log(
                timestamp=when,
                value=value,
                notes=notes,
                tracker_id=record_id,
                user_id=current_user.id,
                added_date_time=now,
            )
            db.session.add(new_log)
            db.session.commit()
            flash(
                "New log added for " + this_tracker.name + " Tracker",
                category="success",
            )
            return redirect(url_for("views.index"))
    except Exception as e:
        print(e)
        flash("Something went wrong!", category="error")
    return render_template(
        "add_log.html", user=current_user, tracker=this_tracker, now=now
    )


@views.route("/view-tracker-logs/<int:record_id>", methods=["GET", "POST"])
@login_required
def view_tracker_logs(record_id):
    from datetime import datetime

    now = datetime.now()
    cur_tracker = Tracker.query.get(record_id)
    logs = Log.query.all()
    try:
        import sqlite3

        basedir = os.path.abspath(os.path.dirname(__file__))
        SQLITE_DB_DIR = os.path.join(basedir, "../db_directory")
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
            SQLITE_DB_DIR, "project.sqlite3"
        )
        conn = sqlite3.connect(os.path.join(SQLITE_DB_DIR, "project.sqlite3"))
        print("Database connected..!!")
        cur = conn.cursor()
        cur.execute(
            "select timestamp,value from log where user_id={} and tracker_id={}".format(
                current_user.id, cur_tracker.id
            )
        )
        data = cur.fetchall()
        print(data)
        dates = []
        values = []
        from dateutil import parser

        for row in data:
            dates.append(parser.parse(row[0]))
            values.append(row[1])
        # dates.sort()
        from matplotlib import style, set_color

        style.use("fivethirtyeight")
        fig = plt.figure(figsize=(18, 8))
        plt.plot_date(dates, values, "-", color="black")
        plt.xlabel("Date and Time")
        plt.ylabel("Values")
        # plt.set_color("black")
        plt.tight_layout()
        plt.savefig("./static/images/graph.png")

        cur.close()
        conn.close()

        return render_template(
            "tracker_logs.html", user=current_user, tracker=cur_tracker, logs=logs
        )
    except Exception as e:
        print(e)
        flash("Something Went Wrong.", category="error")
        return render_template(
            "tracker_logs.html", user=current_user, tracker=cur_tracker, logs=logs
        )


@views.route("/edit-log/<int:record_id>", methods=["GET", "POST"])
@login_required
def edit_log(record_id):
    this_log = Log.query.get(record_id)
    this_tracker = Tracker.query.get(this_log.tracker_id)
    try:
        if request.method == "POST":
            when = request.form.get("date")
            value = request.form.get("value")
            notes = request.form.get("notes")

            this_log.timestamp = when
            this_log.value = value
            this_log.notes = notes

            db.session.commit()
            flash(this_tracker.name + "Log Updated Successfully.", category="success")
            return redirect(
                url_for("views.view_tracker_logs", record_id=this_log.tracker_id)
            )
    except Exception as e:
        print(e)
        flash("Something went wrong.", category="error")
    return render_template(
        "edit_log.html", user=current_user, tracker=this_tracker, log=this_log
    )


@views.route("/delete-log/<int:record_id>", methods=["GET", "POST"])
@login_required
def delete_log(record_id):
    log_details = Log.query.get(record_id)
    tracker_id = log_details.tracker_id
    try:
        db.session.delete(log_details)
        db.session.commit()
        flash("Log deleted Successfully.", category="success")
    except Exception as e:
        print(e)
        flash("Something went wrong.", category="error")
    return redirect(url_for("views.view_tracker_logs", record_id=tracker_id))
