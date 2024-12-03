from app import db


# Lớp Customer (Bảng Customers)
class Customer(db.Model):
    __tablename__ = "Customer"  # Tên bảng trong cơ sở dữ liệu

    CustomerID = db.Column(db.String, primary_key=True)  # Khóa chính
    FirstName = db.Column(db.String, nullable=False)
    LastName = db.Column(db.String, nullable=False)
    DateOfBirth = db.Column(db.Date)
    Role = db.Column(db.String, nullable=False)
    Email = db.Column(db.String, unique=True)
    PhoneNumber = db.Column(db.String, unique=True)
    Address = db.Column(db.String)
    City = db.Column(db.String)
    Country = db.Column(db.String)
    Notes = db.Column(db.String)


# Lớp Account (Bảng Accounts)
class Account(db.Model):
    __tablename__ = "Account"

    AccountID = db.Column(db.String, primary_key=True)  # Khóa chính
    CustomerID = db.Column(
        db.String, db.ForeignKey("Customer.CustomerID"), nullable=False
    )  # Khóa ngoại
    Username = db.Column(db.String, nullable=False)
    Password = db.Column(db.String, nullable=False)
    AccountType = db.Column(db.String)
    Balance = db.Column(db.Integer)  # Dữ liệu kiểu DECIMAL trong MySQL
    DateOpened = db.Column(db.Date)
    accountNumber = db.Column(db.String, unique=True)
    Status = db.Column(db.String)
    PinCode = db.Column(db.String)
    creditScored = db.Column(db.Integer)
    customer = db.relationship(
        "Customer", backref="accounts"
    )  # Tạo quan hệ với Customer


# Lớp Transaction (Bảng Transactions)
class Transaction(db.Model):
    __tablename__ = "Transaction"

    TransactionID = db.Column(db.String, primary_key=True)  # Khóa chính
    senderAccountNumber = db.Column(db.String, nullable=False)  # Khóa ngoại
    recipientAccountNumber = db.Column(db.String, nullable=False)  # Khóa ngoại
    TransactionDate = db.Column(db.DateTime)
    TransactionType = db.Column(db.String)
    Amount = db.Column(db.Numeric(15, 2))  # Dữ liệu kiểu DECIMAL trong MySQL
    Description = db.Column(db.String)


# Lớp CreditScore (Bảng CreditScores)
class CreditScore(db.Model):
    __tablename__ = "CreditScore"

    CustomerID = db.Column(
        db.String, db.ForeignKey("Customer.CustomerID"), primary_key=True
    )  # Khóa ngoại và khóa chính
    CreditScore = db.Column(db.Integer)
    LastUpdated = db.Column(db.Date)
    Description = db.Column(db.String)
