from app.services.account_service import (
    handle_create_account,
    handle_forgot_password,
    handle_reset_password,
    handle_verify_pin,
    handle_send_change_email_pin,
    handle_change_email,
    handle_send_change_password_pin,
    handle_change_password,
    handle_convert_credit_score,
    handle_choose_account_number,
    handle_choose_pin_code,
    handle_get_account_by_account_number,
    handle_confirm_receiver_info,
    handle_confirm_pin_code,
)


from flask import session, redirect, request, flash, render_template, url_for, jsonify
from datetime import date
import uuid


def create_account():
    customer_id = request.args.get("customer_id")
    if request.method == "POST":
        customer_id = request.form["CustomerID"]
        account_data = {
            "AccountID": str(uuid.uuid4()),
            "Username": request.form["Username"],
            "Password": request.form["Password"],
            "AccountType": request.form.get("AccountType", "standard"),
            "Balance": request.form.get("Balance", 50000),
            "Status": request.form.get("Status", "active"),
            "PinCode": request.form.get("PinCode", None),
            "creditScored": request.form.get("creditScored", 0),
            "CustomerID": customer_id,
            "DateOpened": date.today(),
        }
        message, category = handle_create_account(account_data)
        if category == "danger":
            flash(message, category)
            return render_template("create_account.html", customer_id=customer_id)
        else:
            flash("")
            return redirect(url_for("auth.login"))
    return render_template("create_account.html", customer_id=customer_id)


def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        data = {"email": email}
        message, category = handle_forgot_password(data)
        if category == "danger":
            flash(message, category)
            return render_template("forgot_password.html")
        else:
            return render_template("verify_code.html")
    return render_template("forgot_password.html")


def verify_code():
    if request.method == "POST":
        verify_code = request.form.get("verify_code")
        message, category = handle_verify_pin(verify_code)
        if category == "danger":
            flash(message, category)
            return render_template("verify_code.html")
        else:
            session.pop("verification_code", None)
            return render_template("reset_password.html")
    return render_template("verify_code.html")


def reset_password():
    if request.method == "POST":
        new_password = request.form["new_password"]
        confirm_password = request.form["repeat_password"]
        message, category = handle_reset_password(new_password, confirm_password)
        if category == "danger":
            flash(message, category)
            return render_template("reset_password.html")
        else:
            return redirect(url_for("auth.login"))
    return render_template("reset_password.html")


def send_change_email_pin():
    from app.services.account_service import get_detail_account

    account_id = session.get("account_id")
    message, category, [account, customer] = get_detail_account(account_id)
    if request.method == "POST":
        email = request.form["email"]
        message, category = handle_send_change_email_pin(email)
        if category == "danger":
            flash(message, category)
            return redirect(url_for("auth.login"))
    return render_template("change_email.html", customer=customer)


def change_email():

    if request.method == "POST":
        new_email = request.form["new_email"]
        pin_code = request.form["verification_code"]
        message, category = handle_change_email(new_email, pin_code)
        if category == "danger":
            flash(message, category)
            return redirect(url_for("home.change_email"))
        else:
            return redirect(url_for("home.settings"))
    return render_template("change_email.html")


def send_change_password_pin():

    if request.method == "POST":
        email = request.form["email"]
        message, category = handle_send_change_password_pin(email)
        if category == "danger":
            flash(message, category)
            return redirect(url_for("auth.login"))
    return render_template("change_password.html")


def change_password():
    if request.method == "POST":
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]
        pin_code = request.form["verification_code"]
        message, category = handle_change_password(old_password, new_password, pin_code)
        if category == "danger":
            flash(message, category)
            return redirect(url_for("home.change_password"))
        else:
            return redirect(url_for("home.settings"))
    return render_template("change_password.html")


def convert_credit_score():
    if request.method == "POST":
        amount = request.form.get("amount")
        message, category, account = handle_convert_credit_score(amount)
        if category == "danger":
            flash(message, category)
            return redirect(url_for("auth.login"))
        return redirect(url_for("home.credit_score"))
    return render_template("credit_score.html", account=account)


def choose_account_number():
    if request.method == "POST":
        account_number = request.form.get("account_number")
        message, category = handle_choose_account_number(account_number)
        if category == "danger":
            flash(message, category)
            return render_template("choose_account_number.html")
        return redirect(url_for("home.home"))
    return render_template("choose_account_number.html")


def choose_pin_code():
    if request.method == "POST":
        pin_code = request.form.get("pin_code")
        message, category = handle_choose_pin_code(pin_code)
        if category == "danger":
            flash(message, category)
            return render_template("choose_pin_code.html")
        return redirect(url_for("home.transfer_money"))
    return render_template("choose_pin_code.html")


def retrieve_account():
    from app.services.account_service import retrieving_account

    return retrieving_account()


def edit_account(account_id):
    from app.services.account_service import edit_account

    return edit_account(account_id)


def locked_account(account_id):
    from app.services.account_service import locked_account

    return locked_account(account_id)


def unlocked_account(account_id):
    from app.services.account_service import unlocked_account

    return unlocked_account(account_id)


def recharge_account(account_id):
    from app.services.account_service import recharge_account

    return recharge_account(account_id)


def get_account_by_account_number():
    account_number = request.args.get("account_number")
    message, category, account, customer = handle_get_account_by_account_number(
        account_number
    )

    if category == "danger":
        return jsonify({"error": message}), 400

    return (
        jsonify(
            {
                "account": {
                    "accountNumber": account.accountNumber,
                    "balance": account.Balance,
                },
                "customer": {
                    "FirstName": customer.FirstName,
                    "LastName": customer.LastName,
                },
            }
        ),
        200,
    )


def confirm_receiver_info():
    from app.models import Account, Customer
    from app.services.account_service import remove_accents

    if request.method == "POST":
        receiver_account_number = request.form.get("receiver_account_number")
        amount = request.form.get("amount")
        transfer_content = request.form.get("transfer_content")

        (
            message,
            category,
            receiver_account,
            receiver,
            amount,
            transfer_content,
            account,
            customer,
        ) = handle_confirm_receiver_info(
            receiver_account_number, amount, transfer_content
        )
        if category == "danger":
            flash(message, category)
            return redirect(url_for("home.confirm_receiver_info"))
        return render_template(
            "confirm_transfer_info.html",
            receiver_account=receiver_account,
            receiver=receiver,
            amount=amount,
            transfer_content=transfer_content,
            account=account,
            customer=customer,
        )
    account_id = session.get("account_id")
    if not account_id:
        flash("Bạn chưa đăng nhập", "danger")
        return redirect(url_for("auth.login"))
    account = Account.query.filter_by(AccountID=account_id).first()
    if not account:
        flash("Tài khoản không tồn tại", "danger")
        return redirect(url_for("auth.login"))
    customer = Customer.query.filter_by(CustomerID=account.CustomerID).first()
    customer.FirstName = remove_accents(customer.FirstName.upper())
    customer.LastName = remove_accents(customer.LastName.upper())
    return render_template(
        "confirm_receiver_info.html", account=account, customer=customer
    )


def confirm_transfer_info():
    from app.models import Account, Customer

    if request.method == "POST":
        receiver_account = request.form.get("receiver_account")
        receiver = request.form.get("receiver")
        amount = request.form.get("amount")
        transfer_content = request.form.get("transfer_content")
        account = request.form.get("account")
        customer = request.form.get("customer")
        receiver_account = Account.query.filter_by(
            accountNumber=receiver_account
        ).first()
        receiver = Customer.query.filter_by(CustomerID=receiver).first()
        account = Account.query.filter_by(accountNumber=account).first()
        customer = Customer.query.filter_by(CustomerID=customer).first()
        print(
            "\n-------------------------------Check data>>>",
            receiver_account,
            receiver,
            amount,
            transfer_content,
            account,
            customer,
            "--------------------------------\n",
        )
        return render_template(
            "confirm_pin_code.html",
            receiver_account=receiver_account,
            receiver=receiver,
            amount=amount,
            transfer_content=transfer_content,
            account=account,
            customer=customer,
        )
    return render_template(
        "confirm_transfer_info.html",
        receiver_account=None,
        receiver=None,
        amount=None,
        transfer_content=None,
        account=None,
        customer=None,
    )


def confirm_pin_code():
    from app.services.account_service import remove_accents, get_detail_account
    from app.models import Account, Customer

    message, category, [account, customer] = get_detail_account(
        session.get("account_id")
    )
    if category == "danger":
        flash(message, category)
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        receiver_account = request.form.get("receiver_account")
        receiver = request.form.get("receiver")
        amount = request.form.get("amount")
        transfer_content = request.form.get("transfer_content")
        pin_code = request.form.get("pin_code")
        message, category = handle_confirm_pin_code(
            receiver_account,
            receiver,
            amount,
            transfer_content,
            pin_code,
        )
        if category == "danger":
            flash(message, category)
            return render_template(
                "confirm_pin_code.html",
                receiver_account=receiver_account,
                receiver=receiver,
                amount=amount,
                transfer_content=transfer_content,
                account=account,
                customer=customer,
            )
        receiver_account = Account.query.filter_by(
            accountNumber=receiver_account
        ).first()
        receiver = Customer.query.filter_by(CustomerID=receiver).first()
        receiver.FirstName = remove_accents(receiver.FirstName.upper())
        receiver.LastName = remove_accents(receiver.LastName.upper())
        return render_template(
            "transfer_success.html",
            amount=amount,
            receiver_account=receiver_account,
            receiver=receiver,
        )
    return render_template("confirm_pin_code.html")
