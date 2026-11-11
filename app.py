import os
from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = 'super-secret-key-change-this'

# تعديل وتثبيت رابط قاعدة البيانات ليتوافق تماماً مع psycopg و Supabase
db_url = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+psycopg://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}
db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_app_password'
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

mail = Mail(app)

cloudinary.config(
    cloud_name = "md30enow",
    api_key = "435334285529998",
    api_secret = "BcNjtX9xe4br0XyWFsrVtaK3VjU"
)

WHATSAPP_NUMBER = "962797174200"

class AdminSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(200), nullable=False)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(500), nullable=False)

with app.app_context():
    db.create_all()
    admin_pass = AdminSetting.query.filter_by(key='password').first()
    if not admin_pass:
        default_pass = AdminSetting(key='password', value='123456')
        db.session.add(default_pass)
        db.session.commit()

HTML_LAYOUT = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>متجر أم ليليان للمجوهرات</title>
    <link href="https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Tajawal:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #121316;
            --bg-card: #1c1e24;
            --gold-primary: #d4af37;
            --gold-hover: #f3e5ab;
            --bronze-accent: #b87333;
            --text-light: #f4f4f5;
            --text-muted: #a1a1aa;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Tajawal', sans-serif; background-color: var(--bg-dark); color: var(--text-light); line-height: 1.6; }
        h1, h2, h3, .brand-title { font-family: 'Amiri', serif; }
        header { background: linear-gradient(180deg, #1a1c23 0%, var(--bg-dark) 100%); border-bottom: 1px solid rgba(212, 175, 55, 0.2); padding: 18px 8%; display: flex; justify-content: space-between; align-items: center; }
        .brand-title { font-size: 28px; color: var(--gold-primary); text-decoration: none; font-weight: bold; }
        .nav-links a { color: var(--text-light); text-decoration: none; margin-right: 20px; font-size: 15px; transition: color 0.3s; }
        .nav-links a:hover { color: var(--gold-primary); }
        .hero-banner { background: linear-gradient(135deg, #1a1c23 0%, #2a221b 50%, #121316 100%); border-radius: 16px; padding: 50px 30px; text-align: center; margin: 30px 8%; border: 1px solid rgba(212, 175, 55, 0.25); box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5); }
        .hero-banner h1 { font-size: 42px; color: var(--gold-primary); margin-bottom: 12px; }
        .hero-banner p { color: var(--text-muted); font-size: 18px; margin-bottom: 25px; }
        .search-box { max-width: 500px; margin: 0 auto; position: relative; }
        .search-box input { width: 100%; padding: 14px 20px; border-radius: 30px; border: 1px solid rgba(212, 175, 55, 0.4); background-color: rgba(255, 255, 255, 0.05); color: #fff; font-size: 15px; outline: none; }
        .container { padding: 20px 8% 60px 8%; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 25px; margin-top: 30px; }
        .card { background-color: var(--bg-card); border-radius: 14px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.05); transition: transform 0.4s ease; display: flex; flex-direction: column; justify-content: space-between; }
        .card:hover { transform: translateY(-7px) scale(1.02); }
        .card-img-wrapper { width: 100%; height: 250px; overflow: hidden; background-color: #000; }
        .card img { width: 100%; height: 100%; object-fit: cover; }
        .card-body { padding: 20px; text-align: center; }
        .card-title { font-size: 22px; color: #fff; margin-bottom: 8px; }
        .card-price { font-size: 19px; color: var(--gold-primary); font-weight: bold; margin-bottom: 15px; }
        .btn { display: inline-block; padding: 10px 22px; border-radius: 8px; text-decoration: none; font-weight: bold; border: none; cursor: pointer; text-align: center; }
        .btn-gold { background: linear-gradient(45deg, #b87333, #d4af37); color: #121316; width: 100%; }
        .btn-whatsapp { background-color: #25d366; color: #fff; width: 100%; margin-top: 10px; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 14px; }
        .btn-whatsapp:hover { background-color: #20ba5a; }
        .btn-blue { background-color: #2563eb; color: #fff; }
        .btn-danger { background-color: #dc2626; color: #fff; }
        .field { margin-bottom: 18px; text-align: right; }
        .field label { display: block; margin-bottom: 6px; color: var(--text-muted); }
        .field input { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1); background-color: rgba(255, 255, 255, 0.05); color: #fff; }
        form { max-width: 480px; margin: 40px auto; background-color: var(--bg-card); padding: 30px; border-radius: 14px;