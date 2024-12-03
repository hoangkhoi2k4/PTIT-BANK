from flask import Blueprint, session, redirect, url_for, flash
from functools import wraps


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
def admin():
    from app.controllers.user_controller import dashboard
    return dashboard()


@admin_bp.route("/account")
def account_list():
    from app.controllers.account_controller import retrieve_account

    return retrieve_account()


@admin_bp.route("/account/edit/<account_id>", methods=["GET", "POST"])
def edit_account(account_id):
    from app.controllers.account_controller import edit_account

    return edit_account(account_id)


@admin_bp.route("/account/lock/<account_id>")
def lock_account(account_id):
    from app.controllers.account_controller import locked_account

    return locked_account(account_id)


@admin_bp.route("/account/unlock/<account_id>")
def unlock_account(account_id):
    from app.controllers.account_controller import unlocked_account

    return unlocked_account(account_id)


@admin_bp.route("/recharge/<account_id>", methods=["GET", "POST"])
def recharge_account(account_id):
    from app.controllers.account_controller import recharge_account

    return recharge_account(account_id)


# Quản lý người dùng


@admin_bp.route("/user")
def user_list():
    from app.controllers.user_controller import retrieve_user

    return retrieve_user()


@admin_bp.route("/user/edit/<customer_id>", methods=["GET", "POST"])
def edit_user(customer_id):
    from app.controllers.user_controller import update_user

    return update_user(customer_id)


@admin_bp.route("/user/lock/<customer_id>")
def lock_user(customer_id):
    from app.controllers.user_controller import locked_user

    return locked_user(customer_id)


@admin_bp.route("/user/unlock/<customer_id>")
def unlock_user(customer_id):
    from app.controllers.user_controller import unlocked_user

    return unlocked_user(customer_id)


@admin_bp.route("/transaction")
def transaction_list():
    from app.controllers.user_controller import get_transaction

    return get_transaction()
