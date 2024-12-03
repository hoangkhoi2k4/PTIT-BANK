from flask import Blueprint, render_template, session, flash, redirect, url_for


home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def home():
    from app.services.account_service import get_detail_account
    from app.services.account_service import get_latest_transactions

    account_id = session.get("account_id")
    message, category, [account, customer] = get_detail_account(account_id)
    if category == "danger":
        flash(message, category)
        return redirect(url_for("auth.login"))
    transactions = get_latest_transactions(account_id)
    return render_template("home.html", account=account, transactions=transactions)


@home_bp.route("/account/profile")
def profile():
    from app.services.account_service import handle_get_profile, remove_accents

    message, category, account, customer = handle_get_profile()
    if category == "danger":
        flash(message, category)
        return redirect(url_for("auth.login"))
    customer.FirstName = remove_accents(customer.FirstName.upper())
    customer.LastName = remove_accents(customer.LastName.upper())
    return render_template("profile.html", account=account, customer=customer)


@home_bp.route("/account/transfer-money")
def transfer_money():
    from app.services.account_service import get_detail_account, remove_accents

    account_id = session.get("account_id")
    message, category, [account, customer] = get_detail_account(account_id)
    if category == "danger":
        flash(message, category)
        return redirect(url_for("auth.login"))
    customer.FirstName = remove_accents(customer.FirstName.upper())
    customer.LastName = remove_accents(customer.LastName.upper())
    return render_template("transfer_money.html", account=account, customer=customer)


@home_bp.route("/account/credit-score")
def credit_score():
    from app.services.account_service import get_detail_account

    account_id = session.get("account_id")
    message, category, [account, customer] = get_detail_account(account_id)
    if category == "danger":
        flash(message, category)
        return redirect(url_for("auth.login"))
    return render_template("credit_score.html", account=account)


@home_bp.route("/account/settings")
def settings():
    from app.services.account_service import get_detail_account

    account_id = session.get("account_id")
    message, category, [account, customer] = get_detail_account(account_id)
    if category == "danger":
        flash(message, category)
        return redirect(url_for("auth.login"))
    if customer:
        return render_template("settings.html", customer=customer)
    return render_template("settings.html", customer=customer)


@home_bp.route("/account/send-change-email-pin", methods=["POST", "GET"])
def send_change_email_pin():
    from app.controllers.account_controller import send_change_email_pin

    return send_change_email_pin()


@home_bp.route("/account/change-email", methods=["POST", "GET"])
def change_email():
    from app.controllers.account_controller import change_email

    return change_email()


@home_bp.route("/account/send-change-password-pin", methods=["POST", "GET"])
def send_change_password_pin():
    from app.controllers.account_controller import send_change_password_pin

    return send_change_password_pin()


@home_bp.route("/account/change-password", methods=["POST", "GET"])
def change_password():
    from app.controllers.account_controller import change_password

    return change_password()


@home_bp.route("/account/convert-credit-score", methods=["POST", "GET"])
def convert_credit_score():
    from app.controllers.account_controller import convert_credit_score

    return convert_credit_score()


@home_bp.route("/account/choose-account-number", methods=["POST", "GET"])
def choose_account_number():
    from app.controllers.account_controller import choose_account_number

    return choose_account_number()


@home_bp.route("/account/choose-pin-code", methods=["POST", "GET"])
def choose_pin_code():
    from app.controllers.account_controller import choose_pin_code

    return choose_pin_code()


@home_bp.route("/api/get-account-by-account-number", methods=["GET"])
def get_account_by_account_number():
    from app.controllers.account_controller import get_account_by_account_number

    return get_account_by_account_number()


@home_bp.route("/account/transfer-money/confirm-receiver-info", methods=["GET", "POST"])
def confirm_receiver_info():
    from app.controllers.account_controller import confirm_receiver_info

    return confirm_receiver_info()


@home_bp.route(
    "/account/transfer-money/confirm-transfer-information", methods=["POST", "GET"]
)
def confirm_transfer_information():
    from app.controllers.account_controller import confirm_transfer_info

    return confirm_transfer_info()


@home_bp.route("/account/transfer-money/confirm-pin-code", methods=["GET", "POST"])
def confirm_pin_code():
    from app.controllers.account_controller import confirm_pin_code

    return confirm_pin_code()


@home_bp.route("/account/transfer_money/success", methods=["GET", "POST"])
def transfer_success():
    return render_template("transfer_success.html")


@home_bp.route("/account/get-transaction", methods=["POST", "GET"])
def get_transaction():
    from app.services.account_service import get_transaction

    return get_transaction()
