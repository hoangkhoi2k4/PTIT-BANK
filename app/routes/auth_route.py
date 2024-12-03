from flask import Blueprint, session, redirect, url_for, flash


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    from app.controllers.user_controller import login

    return login()


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    from app.controllers.user_controller import create_user

    return create_user()


@auth_bp.route("/register/create-account", methods=["GET", "POST"])
def create_account():
    from app.controllers.account_controller import create_account

    return create_account()


@auth_bp.route("/login/forgot-password", methods=["POST", "GET"])
def forgot_password():
    from app.controllers.account_controller import forgot_password

    return forgot_password()


@auth_bp.route("/login/verify-code", methods=["POST", "GET"])
def verify_code():
    from app.controllers.account_controller import verify_code

    return verify_code()


@auth_bp.route("/login/reset-password", methods=["POST", "GET"])
def reset_password():
    from app.controllers.account_controller import reset_password

    return reset_password()


@auth_bp.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()
    flash("Bạn đã đăng xuất thành công.", "success")
    return redirect(url_for("auth.login"))
