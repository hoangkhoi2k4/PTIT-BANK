from app.services.user_service import (
    handle_create_user,
    handle_login,
)

from flask import request, flash, redirect, url_for, session, render_template
import uuid


def create_user():
    if request.method == "POST":
        data = {
            "customer_id": str(uuid.uuid4()),
            "first_name": request.form["FirstName"],
            "last_name": request.form["LastName"],
            "date_of_birth": request.form.get("DateOfBirth"),
            "role": "user",
            "email": request.form["Email"],
            "phone_number": request.form["PhoneNumber"],
            "address": request.form.get("Address"),
            "city": request.form.get("City"),
            "country": request.form.get("Country"),
            "notes": request.form.get("Notes"),
        }
        message, category, customer_id = handle_create_user(data)
        if category == "danger":
            flash(message, category)
            return render_template("register.html")
        else:
            flash("")
            return redirect(url_for("auth.create_account", customer_id=customer_id))
    return render_template("register.html")


def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        message, category, account_id = handle_login(username, password)
        if category == "danger":
            flash(message, category)
            return redirect(url_for("auth.login"))
        elif category == "warning":
            return render_template("login.html", is_open_popup=True, message=message)
        else:
            session["account_id"] = account_id
            flash("")
            return redirect(url_for("home.home"))
    return render_template("login.html", is_open_popup=False)


def dashboard():
    from app.services.user_service import dashboard

    return dashboard()


def retrieve_user():
    from app.services.user_service import retrieve_user

    return retrieve_user()


def update_user(customer_id):
    from app.services.user_service import update_user

    return update_user(customer_id)


def locked_user(customer_id):
    from app.services.user_service import locked_user

    return locked_user(customer_id)


def unlocked_user(customer_id):
    from app.services.user_service import unlocked_user

    return unlocked_user(customer_id)


def get_transaction():
    from app.services.user_service import get_transaction

    return get_transaction()
