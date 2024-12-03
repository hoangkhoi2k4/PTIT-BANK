import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "hhtrinh2505@gmail.com"
SENDER_PASSWORD = "gslj zyxq baxt ekqg"


def setup_email_server():
    """Thiết lập kết nối đến máy chủ SMTP."""
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    return server


def create_email_message(subject, body, recipient_email, is_html=False):
    """Tạo đối tượng email với tiêu đề và nội dung."""
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = recipient_email
    message["Subject"] = subject

    # Chọn kiểu nội dung: HTML hoặc plain text
    mime_type = "html" if is_html else "plain"
    message.attach(MIMEText(body, mime_type))

    return message


def send_verification_email_service(email, verification_code, subject):
    subject = subject
    body = f"Mã xác thực của bạn là: {verification_code}"

    # Tạo email và gửi
    message = create_email_message(subject, body, email, is_html=False)
    try:
        with setup_email_server() as server:
            server.sendmail(SENDER_EMAIL, email, message.as_string())
            return "Mã xác thực đã được gửi tới email của bạn", "success"
    except Exception as e:
        return f"An error occurred: {str(e)}", "danger"


def send_transaction_email(user_email, transaction_details, is_plus):
    subject = "BIẾN ĐỘNG SỐ DƯ"

    # Chọn màu dựa trên giá trị isPlus
    amount_color = "blue" if is_plus else "red"

    body = f"""
    <html>
        <body>
            <p>Xin chào,</p>
            <p>Giao dịch của bạn đã được thực hiện thành công.</p>
            <p><b>Thông tin giao dịch:</b></p>
            <ul>
                <li>Người nhận: {transaction_details['recipient_name']}</li>
                <li>Số tài khoản người nhận: {transaction_details['recipient_account']}</li>
                <li>
                    Số tiền: 
                    <span style="color: {amount_color}; font-weight: bold;">
                        {transaction_details['amount']} VND
                    </span>
                </li>
                <li>Nội dung: {transaction_details['content']}</li>
                <li>Ngày giao dịch: {transaction_details['transaction_date']}</li>
            </ul>
            <p>Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi.</p>
        </body>
    </html>
    """

    # Tạo email và gửi
    message = create_email_message(subject, body, user_email, is_html=True)
    try:
        with setup_email_server() as server:
            server.sendmail(SENDER_EMAIL, user_email, message.as_string())
            print("Email thông báo giao dịch đã được gửi thành công.")
    except Exception as e:
        print("Không thể gửi email thông báo giao dịch. Lỗi:", e)


def send_receive_transaction_email(user_email, transaction_details, is_plus):
    subject = "BIẾN ĐỘNG SỐ DƯ"

    # Chọn màu dựa trên giá trị isPlus
    amount_color = "blue" if is_plus else "red"

    body = f"""
    <html>
        <body>
            <p>Xin chào,</p>
            <p>Giao dịch của bạn đã được thực hiện thành công.</p>
            <p><b>Thông tin giao dịch:</b></p>
            <ul>
                <li>Người gửi: {transaction_details['sender_name']}</li>
                <li>Số tài khoản người gửi: {transaction_details['sender_account']}</li>
                <li>
                    Số tiền: 
                    <span style="color: {amount_color}; font-weight: bold;">
                        {transaction_details['amount']} VND
                    </span>
                </li>
                <li>Nội dung: {transaction_details['content']}</li>
                <li>Ngày giao dịch: {transaction_details['transaction_date']}</li>
            </ul>
            <p>Cảm ơn bạn đã sử dụng dịch vụ của chúng tôi.</p>
        </body>
    </html>
    """

    # Tạo email và gửi
    message = create_email_message(subject, body, user_email, is_html=True)
    try:
        with setup_email_server() as server:
            server.sendmail(SENDER_EMAIL, user_email, message.as_string())
            print("Email thông báo giao dịch đã được gửi thành công.")
    except Exception as e:
        print("Không thể gửi email thông báo giao dịch. Lỗi:", e)
