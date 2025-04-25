from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    passport_series = db.Column(db.String(10))
    passport_number = db.Column(db.String(20))
    passport_issued_by = db.Column(db.String(200))
    passport_issue_date = db.Column(db.Date)
    passport_image = db.Column(db.String(100))  # Путь к скану паспорта
    profile_image = db.Column(db.String(100))   # Путь к фото профиля
    tours = db.relationship('Tour', backref='client', lazy=True)

class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    duration = db.Column(db.String(50), nullable=False)  # например, "7 дней/6 ночей"
    price = db.Column(db.Float, nullable=False)
    
    tours = db.relationship('Tour', backref='route', lazy=True)

class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # например, "забронирован", "оплачен", "отменен"