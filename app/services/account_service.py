import random
import string
import re
import unicodedata
import pytz
from decimal import Decimal
import uuid
from datetime import datetime, timezone
from sqlalchemy import case, or_, desc
from sqlalchemy.orm import aliased


from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models import Account, Customer, Transaction

vietnam_tz = pytz.timezone("Asia/Ho_Chi_Minh")

from app.controllers.email_controller import (
    send_verification_email,
)


def is_strong_password(password):
    message, category = "", ""
    if len(password) < 8:
        message, category = "Mật khẩu phải có ít nhất 8 ký tự.", "danger"
    elif not any(char.isupper() for char in password):
        message, category = "Mật khẩu phải có ít nhất 1 chữ cái viết hoa.", "danger"
    elif not any(char.islower() for char in password):
        message, category = "Mật khẩu phải có ít nhất 1 chữ cái viết thường.", "danger"
    elif not any(char.isdigit() for char in password):
        message, category = "Mật khẩu phải có ít nhất 1 chữ số.", "danger"
    elif not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        message, category = "Mật khẩu phải có ít nhất 1 ký tự đặc biệt.", "danger"
    elif any(char.isspace() for char in password):
        message, category = "Mật khẩu không được chứa khoảng trắng.", "danger"
    else:
        message, category = "Mật khẩu hợp lệ.", "success"
    return message, category


def handle_create_account(data):
    exist_username_account = Account.query.filter_by(Username=data["Username"]).first()
    if exist_username_account:
        return "Tên đăng nhập đã tồn tại", "danger"
    if "Password" in data:
        message, category = is_strong_password(data["Password"])
        if category == "danger":
            return message, category
        data["Password"] = generate_password_hash(data["Password"])
    new_account = Account(**data)
    try:
        db.session.add(new_account)
        db.session.commit()
        return "Account created successfully!", "success"
    except Exception as e:
        db.session.rollback()
        return f"An error occurred: {str(e)}", "danger"


def get_detail_account(account_id):
    if not account_id:
        return "Bạn chưa đăng nhập", "danger", [None, None]

    # Truy vấn thông tin tài khoản từ DB dựa trên account_id
    account = Account.query.get(account_id)
    if not account:
        return "Tài khoản không tồn tại", "danger", [None, None]
    customer = Customer.query.filter_by(CustomerID=account.CustomerID).first()
    return "", "success", [account, customer]


# Lưu số tài khoản người dùng chọn vào database
def set_account_number(account_number):
    account_info = session.get("new_account")
    if not account_info:
        flash("Không tìm thấy thông tin tài khoản ", "danger")
        return redirect(url_for("auth.register"))
    account_id = account_info["AccountID"]
    # Cập nhật số tài khoản trong cơ sở dữ liệu
    account = Account.query.get(account_id)
    if account:
        account.accountNumber = account_number
        db.session.commit()
        flash("Số tài khoản đã được chọn thành công!", "success")
        return redirect(url_for("dashboard"))
    else:
        flash("Lỗi khi chọn số tài khoản.", "danger")
        return redirect(url_for("choose_account_number"))


def handle_forgot_password(data):
    # Tìm tài khoản theo email
    customer = Customer.query.filter_by(Email=data["email"]).first()
    if customer:
        account = Account.query.filter_by(CustomerID=customer.CustomerID).first()

        # Tạo mã xác thực ngẫu nhiên
        verification_code = str(random.randint(100000, 999999))

        # Lưu mã xác thực và ID tài khoản vào session
        session["verification_code"] = verification_code
        session["account_id"] = account.AccountID

        # Gửi email xác thực
        message, category = send_verification_email(
            data["email"], verification_code, "MÃ XÁC THỰC ĐỔI MẬT KHẨU"
        )

        return message, category
    else:
        # Email không tồn tại trong hệ thống
        return "Email không tồn tại trong hệ thống.", "danger"


def handle_verify_pin(verify_code):
    verification_code = session["verification_code"]
    if verification_code == verify_code:
        return "Mã xác thực chính xác", "success"
    else:
        return "Mã xác thực không đúng, vui lòng kiểm tra lại!", "danger"


def handle_reset_password(new_password, confirm_password):

    if new_password != confirm_password:
        return "Mật khẩu mới và mật khẩu nhập lại không khớp.", "danger"

    # Kiểm tra mã xác thực
    account_id = session.get("account_id")
    account = Account.query.get(account_id)

    if account:
        # Hash và lưu mật khẩu mới
        hashed_password = generate_password_hash(new_password)
        account.Password = hashed_password
        db.session.commit()

        # Xóa ID tài khoản khỏi session
        session.pop("account_id", None)

        return "Mật khẩu đã được thay đổi thành công.", "success"
    else:
        return "Tài khoản không tồn tại.", "danger"


def handle_send_change_email_pin(email):
    if email:
        verification_code = str(random.randint(100000, 999999))
        # Lưu mã xác thực và ID tài khoản vào session
        session["verification_code"] = verification_code
        # Gửi email xác thực
        message, category = send_verification_email(
            email, verification_code, "MÃ XÁC THỰC ĐỔI EMAIL"
        )
        return message, category
    else:
        return "Bạn chưa đăng nhập", "danger"


def handle_change_email(new_email, verify_code):
    verification_code = session["verification_code"]
    if verification_code == verify_code:
        # Kiểm tra email đã tồn tại hay chưa
        if Customer.query.filter_by(Email=new_email).first():
            return "Email đã tồn tại trong hệ thống.", "danger"
        else:
            account_id = session.get("account_id")
            account = Account.query.get(account_id)
            if account:
                customer = Customer.query.filter_by(
                    CustomerID=account.CustomerID
                ).first()
                if customer:
                    customer.Email = new_email
                    db.session.commit()
                    return "Email đã được thay đổi thành công!", "success"
    return "Mã xác thực không chính xác, vui lòng thử lại", "danger"


def handle_send_change_password_pin(email):
    if email:
        verification_code = str(random.randint(100000, 999999))
        # Lưu mã xác thực và ID tài khoản vào session
        session["verification_code"] = verification_code
        # Gửi email xác thực
        message, category = send_verification_email(
            email, verification_code, "MÃ XÁC THỰC ĐỔI MẬT KHẨU"
        )
        return message, category
    else:
        return "Bạn chưa đăng nhập", "danger"


def handle_change_password(old_password, new_password, verify_code):
    account_id = session.get("account_id")
    if not account_id:
        return "Bạn chưa đăng nhập", "danger"
    account = Account.query.get(account_id)
    if not account:
        return "Tài khoản không tồn tại", "danger"
    if not check_password_hash(account.Password, old_password):
        return "Mật khẩu cũ không chính xác", "danger"
    verification_code = session.get("verification_code")
    if not verification_code or verification_code != verify_code:
        return "Mã xác thực không chính xác", "danger"
    hashed_new_password = generate_password_hash(new_password)

    account.Password = hashed_new_password
    db.session.commit()

    session.pop("verification_code", None)

    return "Đổi mật khẩu thành công", "success"


def handle_convert_credit_score(amount):
    account_id = session.get("account_id")
    if not account_id:
        return "Bạn chưa đăng nhập", "danger", None
    account = Account.query.filter_by(AccountID=account_id).first()
    if not account:
        return "Tài khoản không tồn tại", "danger", None
    account.creditScored -= int(amount)
    db.session.commit()
    return "Đổi điểm thưởng thành công!", "success", account


def handle_get_profile():
    account_id = session.get("account_id")
    if not account_id:
        return "Bạn chưa đăng nhập", "danger", None, None
    account = Account.query.filter_by(AccountID=account_id).first()
    if not account:
        return "Tài khoản không tồn tại", "danger", None, None
    customer = Customer.query.filter_by(CustomerID=account.CustomerID).first()
    return "Thông tin tài khoản", "success", account, customer


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def handle_choose_account_number(account_number):
    account_id = session.get("account_id")
    if not account_id:
        return "Bạn chưa đăng nhập", "danger"
    account = Account.query.filter_by(AccountID=account_id).first()
    if not account:
        return "Tài khoản không tồn tại", "danger"
    if not account_number:
        return "Số tài khoản không thể trống", "danger"
    if not account_number.isdigit():
        return "Số tài khoản chỉ bao gồm các chữ số", "danger"
    if len(account_number) < 8 or len(account_number) > 16:
        return "Số tài khoản phải có ít nhất 8 và nhiều nhất 16 chữ số", "danger"
    if " " in account_number:
        return "Số tài khoản không được có khoảng trắng", "danger"
    existing_account = Account.query.filter_by(accountNumber=account_number).first()
    if existing_account:
        return "Số tài khoản đã tồn tại", "danger"
    account.accountNumber = account_number
    db.session.commit()
    return "Chọn tài khoản thành công", "success"


def handle_choose_pin_code(pin_code):
    account_id = session.get("account_id")
    if not account_id:
        return "Bạn chưa đăng nhập", "danger"
    account = Account.query.filter_by(AccountID=account_id).first()
    if not account:
        return "Tài khoản không tồn tại", "danger"
    if not pin_code:
        return "Mã pin không thể trống", "danger"
    if not pin_code.isdigit():
        return "Mã pin chỉ bao gồm các chữ số", "danger"
    if len(pin_code) != 6:
        return "Mã pin phải có đúng 6 chữ số!", "danger"
    if " " in pin_code:
        return "Mã pin không được có khoảng trắng", "danger"
    account.PinCode = pin_code
    db.session.commit()
    return "Thiết lập mã pin thành công!", "success"


def check_role():
    account_id = session.get("account_id")
    if not account_id:
        return "Bạn chưa đăng nhập", "danger"

    account = Account.query.filter_by(AccountID=account_id).first()
    if not account:
        return "Tài khoản không tồn tại", "danger"

    customer = Customer.query.filter_by(CustomerID=account.CustomerID).first()
    if not customer:
        return "Khách hàng không tồn tại", "danger"

    if customer.Role != "Admin":
        return "Bạn không có quyền truy cập trang này", "danger"

    return "Welcome Admin", "success"


def retrieving_account():
    message, category = check_role()
    if category == "danger":
        flash(message, category)
        return redirect(url_for("auth.login"))
    page = request.args.get("page", 1, type=int)  # Default to page 1
    per_page = 8  # 8 accounts per page

    pagination = Account.query.paginate(page=page, per_page=per_page, error_out=False)
    accounts = pagination.items

    return render_template(
        "admin/account/account.html", accounts=accounts, pagination=pagination
    )


def edit_account(account_id):
    message, category = check_role()
    if category == "danger":
        flash(message, category)
        return redirect(url_for("auth.login"))
    account = Account.query.get(account_id)  # Lấy thông tin tài khoản từ DB
    if not account:
        return "Account not found", 404

    if request.method == "POST":
        # Cập nhật các thuộc tính từ form
        account.Username = request.form["Username"]
        account.Password = request.form["Password"]
        account.AccountType = request.form["AccountType"]
        account.Balance = request.form["Balance"]
        account.AccountType = request.form["AccountType"]
        account.Status = request.form.get("Status", account.Status)
        account.PinCode = request.form.get("PinCode", account.PinCode)
        account.creditScored = request.form.get("creditScored", account.creditScored)

        db.session.commit()  # Lưu thay đổi vào DB
        return redirect(url_for("admin.account_list"))

    return render_template("admin/account/edit.html", account=account)


def locked_account(account_id):
    message, category = check_role()
    if category == "danger":
        flash(message, category)
        return redirect(url_for("auth.login"))
    account = Account.query.get(account_id)  # Lấy thông tin tài khoản từ DB
    if not account:
        return "Account not found", 404

    account.Status = "Locked"
    db.session.commit()  # Xóa tài khoản khỏi DB
    return redirect(url_for("admin.account_list"))


def unlocked_account(account_id):
    message, category = check_role()
    if category == "danger":
        flash(message, category)
        return redirect(url_for("auth.login"))
    account = Account.query.get(account_id)  # Lấy thông tin tài khoản từ DB
    if not account:
        return "Account not found", 404

    account.Status = "Active"
    db.session.commit()  # Xóa tài khoản khỏi DB
    return redirect(url_for("admin.account_list"))


def recharge_account(account_id):
    message, category = check_role()
    if category == "danger":
        flash(message, category)
        return redirect(url_for("auth.login"))

    account = Account.query.get(account_id)  # Lấy thông tin tài khoản từ DB
    if not account:
        return "Account not found", 404

    if request.method == "POST":
        amount = float(request.form["amount"])  # Chuyển đổi Decimal thành float
        account.Balance += amount
        db.session.commit()  # Lưu thay đổi vào DB
        return redirect(url_for("admin.account_list"))

    return render_template("admin/account/recharge.html", account=account)


def handle_get_account_by_account_number(account_number):
    if not account_number:
        return "Vui lòng nhập số tài khoản!", "danger", None, None
    account = Account.query.filter_by(accountNumber=account_number).first()
    if not account:
        return "Tài khoản không tồn tại!", "danger", None, None
    customer = Customer.query.filter_by(CustomerID=account.CustomerID).first()
    if not customer:
        return "Không tìm thấy thông tin khách hàng!", "danger", None, None
    customer.FirstName = remove_accents(customer.FirstName.upper())
    customer.LastName = remove_accents(customer.LastName.upper())
    return "Thông tin tài khoản", "success", account, customer


def handle_confirm_receiver_info(receiver_account_number, amount, transfer_content):
    account_id = session.get("account_id")
    account = Account.query.filter_by(AccountID=account_id).first()
    customer = Customer.query.filter_by(CustomerID=account.CustomerID).first()
    if not receiver_account_number:
        return (
            "Vui lòng nhập số tài khoản nhận!",
            "danger",
            None,
            None,
            None,
            None,
            None,
            None,
        )
    if receiver_account_number == account.accountNumber:
        return (
            "Bạn không thể giao dịch với chính mình!",
            "danger",
            None,
            None,
            None,
            None,
            None,
            None,
        )
    if not amount:
        return (
            "Vui lòng nhập số tiền giao dịch!",
            "danger",
            None,
            None,
            None,
            None,
            None,
            None,
        )
    if int(amount.replace(",", "")) > account.Balance:
        return (
            "Số dư của bạn không đủ!",
            "danger",
            None,
            None,
            None,
            None,
            None,
            None,
        )
    receiver_account = Account.query.filter_by(
        accountNumber=receiver_account_number
    ).first()
    receiver = Customer.query.filter_by(CustomerID=receiver_account.CustomerID).first()
    customer.FirstName = remove_accents(customer.FirstName.upper())
    customer.LastName = remove_accents(customer.LastName.upper())
    receiver.FirstName = remove_accents(receiver.FirstName.upper())
    receiver.LastName = remove_accents(receiver.LastName.upper())
    return (
        "",
        "success",
        receiver_account,
        receiver,
        amount,
        transfer_content,
        account,
        customer,
    )


def handle_confirm_pin_code(
    receiver_account, receiver, amount, transfer_content, pin_code
):
    from app.services.email_service import (
        send_transaction_email,
        send_receive_transaction_email,
    )

    receiver_account = Account.query.filter_by(accountNumber=receiver_account).first()
    receiver = Customer.query.filter_by(CustomerID=receiver).first()
    account_id = session.get("account_id")
    if not account_id:
        return "Bạn chưa đăng nhập", "danger"
    account = Account.query.filter_by(AccountID=account_id).first()
    customer = Customer.query.filter_by(CustomerID=account.CustomerID).first()
    if not account:
        return "Tài khoản không tồn tại", "danger"
    if not pin_code:
        return "Vui lòng nhập mã pin!", "danger"
    if account.PinCode != pin_code:
        return "Mã pin không đúng!", "danger"
    amount = int(amount.replace(",", ""))
    try:
        receiver_account.Balance += amount

        account.Balance -= amount

        account.creditScored += 100

        transaction = Transaction(
            TransactionID=str(uuid.uuid4()),  # Tạo ID giao dịch duy nhất
            senderAccountNumber=account.accountNumber,
            recipientAccountNumber=receiver_account.accountNumber,
            TransactionDate=datetime.now(vietnam_tz),
            TransactionType="Transfer Money",
            Amount=amount,
            Description=transfer_content,
        )
        customer.FirstName = remove_accents(customer.FirstName.upper())
        customer.LastName = remove_accents(customer.LastName.upper())
        receiver.FirstName = remove_accents(receiver.FirstName.upper())
        receiver.LastName = remove_accents(receiver.LastName.upper())

        customer_transaction_details = {
            "recipient_name": receiver.FirstName + " " + receiver.LastName,
            "recipient_account": receiver_account.accountNumber,
            "amount": "- " + str(amount),
            "content": transfer_content,
            "transaction_date": transaction.TransactionDate,
        }

        receiver_transaction_details = {
            "sender_name": customer.FirstName + " " + customer.LastName,
            "sender_account": account.accountNumber,
            "amount": "+ " + str(amount),
            "content": transfer_content,
            "transaction_date": transaction.TransactionDate,
        }

        db.session.add(transaction)

        db.session.commit()

        send_transaction_email(
            customer.Email, customer_transaction_details, is_plus=False
        )
        send_receive_transaction_email(
            receiver.Email, receiver_transaction_details, is_plus=True
        )

        return "Giao dịch thành công!", "success"
    except Exception as e:
        db.session.rollback()
        print(e)
        return (
            "Có lỗi xảy ra khi thực hiện giao dịch. Vui lòng thử lại!",
            "danger",
        )


def get_latest_transactions(account_id, limit=5):
    # Định nghĩa alias cho Account (người nhận)
    RecipientAccount = aliased(Account)
    account_number = (
        Account.query.with_entities(Account.accountNumber)
        .filter_by(AccountID=account_id)
        .first()[0]
    )

    # Truy vấn giao dịch
    transactions = (
        db.session.query(
            Transaction,
            Account.Username.label("sender_username"),
            Customer.FirstName.label("recipient_first_name"),
            Customer.LastName.label("recipient_last_name"),
            RecipientAccount.accountNumber.label("recipient_account_number"),
        )
        .join(Account, Transaction.senderAccountNumber == Account.accountNumber)
        .join(
            RecipientAccount,
            Transaction.recipientAccountNumber == RecipientAccount.accountNumber,
        )
        .join(Customer, RecipientAccount.CustomerID == Customer.CustomerID)
        .filter(Transaction.senderAccountNumber == account_number)
        .order_by(desc(Transaction.TransactionDate))
        .limit(limit)
        .all()
    )

    # Xử lý kết quả để gộp FirstName và LastName thành Name
    result = []
    for (
        txn,
        sender_username,
        first_name,
        last_name,
        recipient_account_number,
    ) in transactions:
        recipient_name = (
            f"{first_name} {last_name}"
            if first_name and last_name
            else "Không xác định"
        )
        result.append(
            (txn, sender_username, recipient_name, recipient_account_number)
        )  # Trả về tuple phù hợp với template

    return result


def get_transaction():
    account_id = session.get("account_id")
    if not account_id:
        flash("Bạn chưa đăng nhập", "danger")
        return redirect(url_for("login"))

    # Truy vấn thông tin tài khoản và khách hàng
    account = Account.query.get(account_id)
    customer = Customer.query.get(account.CustomerID)
    transactions = None  # Khởi tạo biến transactions

    if request.method == "POST":
        start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d")
        end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d")

        # Định nghĩa alias cho Account và Customer
        SenderAccount = aliased(Account)
        RecipientAccount = aliased(Account)
        SenderCustomer = aliased(Customer)
        RecipientCustomer = aliased(Customer)

        # Lấy số trang hiện tại
        page = request.args.get("page", 1, type=int)

        # Truy vấn giao dịch với phân trang
        transactions = (
            db.session.query(
                Transaction,
                SenderCustomer.FirstName.label("sender_first_name"),
                SenderCustomer.LastName.label("sender_last_name"),
                RecipientCustomer.FirstName.label("recipient_first_name"),
                RecipientCustomer.LastName.label("recipient_last_name"),
                RecipientAccount.accountNumber.label("recipient_account_number"),
                Transaction.senderAccountNumber,
                Transaction.recipientAccountNumber,
                # Xác định loại giao dịch
                case(
                    (
                        Transaction.senderAccountNumber == account.accountNumber,
                        "outgoing",
                    ),
                    else_="incoming",
                ).label("transaction_type"),
            )
            .join(
                SenderAccount,
                Transaction.senderAccountNumber == SenderAccount.accountNumber,
            )
            .join(
                RecipientAccount,
                Transaction.recipientAccountNumber == RecipientAccount.accountNumber,
            )
            .join(SenderCustomer, SenderAccount.CustomerID == SenderCustomer.CustomerID)
            .join(
                RecipientCustomer,
                RecipientAccount.CustomerID == RecipientCustomer.CustomerID,
            )
            .filter(
                or_(
                    Transaction.senderAccountNumber == account.accountNumber,
                    Transaction.recipientAccountNumber == account.accountNumber,
                ),
                Transaction.TransactionDate.between(start_date, end_date),
            )
            .order_by(desc(Transaction.TransactionDate))
            .paginate(page=page, per_page=10, error_out=False)
        )

    return render_template(
        "profile.html", transactions=transactions, account=account, customer=customer
    )
