import os
from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = 'super-secret-key-change-this'

# إعدادات قاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# إعدادات البريد الإلكتروني لاستعادة الباسورد
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'     # ضع بريدك الإلكتروني هنا
app.config['MAIL_PASSWORD'] = 'your_app_password'        # ضع كلمة مرور التطبيق من قوقل هنا
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'

mail = Mail(app)

# ==========================================
# إعدادات Cloudinary لرفع وحفظ الصور سحابياً
# ==========================================
cloudinary.config(
    cloud_name = "md30enow",
    api_key = "435334285529998",
    api_secret = "BcNjtX9xe4br0XyWFsrVtaK3VjU" # ضع الرمز السري الخاص بك هنا
)

# جدول لتخزين إعدادات الأدمن (مثل كلمة المرور والبريد المعتمد)
class AdminSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(200), nullable=False)

# نموذج قطع المجوهرات
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(500), nullable=False)

with app.app_context():
    db.create_all()
    # إنشاء كلمة مرور افتراضية (123456) إذا لم تكن موجودة مسبقاً
    admin_pass = AdminSetting.query.filter_by(key='password').first()
    if not admin_pass:
        default_pass = AdminSetting(key='password', value='123456')
        db.session.add(default_pass)
        db.session.commit()

# القالب الأساسي والتصميم (HTML + CSS)
HTML_LAYOUT = """
<!DOCTYPE html>
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

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Tajawal', sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-light);
            line-height: 1.6;
        }

        h1, h2, h3, .brand-title {
            font-family: 'Amiri', serif;
        }

        header {
            background: linear-gradient(180deg, #1a1c23 0%, var(--bg-dark) 100%);
            border-bottom: 1px solid rgba(212, 175, 55, 0.2);
            padding: 18px 8%;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .brand-title {
            font-size: 28px;
            color: var(--gold-primary);
            text-decoration: none;
            font-weight: bold;
            letter-spacing: 0.5px;
        }

        .nav-links a {
            color: var(--text-light);
            text-decoration: none;
            margin-right: 20px;
            font-size: 15px;
            transition: color 0.3s;
        }

        .nav-links a:hover {
            color: var(--gold-primary);
        }

        .hero-banner {
            background: linear-gradient(135deg, #1a1c23 0%, #2a221b 50%, #121316 100%);
            border-radius: 16px;
            padding: 50px 30px;
            text-align: center;
            margin: 30px 8%;
            border: 1px solid rgba(212, 175, 55, 0.25);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
        }

        .hero-banner h1 {
            font-size: 42px;
            color: var(--gold-primary);
            margin-bottom: 12px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.6);
        }

        .hero-banner p {
            color: var(--text-muted);
            font-size: 18px;
            margin-bottom: 25px;
        }

        .search-box {
            max-width: 500px;
            margin: 0 auto;
            position: relative;
        }

        .search-box input {
            width: 100%;
            padding: 14px 20px;
            border-radius: 30px;
            border: 1px solid rgba(212, 175, 55, 0.4);
            background-color: rgba(255, 255, 255, 0.05);
            color: #fff;
            font-size: 15px;
            outline: none;
            transition: all 0.3s;
        }

        .search-box input:focus {
            border-color: var(--gold-primary);
            box-shadow: 0 0 12px rgba(212, 175, 55, 0.3);
            background-color: rgba(0, 0, 0, 0.3);
        }

        .container {
            padding: 20px 8% 60px 8%;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }

        .card {
            background-color: var(--bg-card);
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: transform 0.4s ease, box-shadow 0.4s ease, border-color 0.4s ease;
        }

        .card:hover {
            transform: translateY(-7px) scale(1.02);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6), 0 0 15px rgba(212, 175, 55, 0.2);
            border-color: rgba(212, 175, 55, 0.4);
        }

        .card-img-wrapper {
            width: 100%;
            height: 250px;
            overflow: hidden;
            background-color: #000;
        }

        .card img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.5s ease;
        }

        .card:hover img {
            transform: scale(1.08);
        }

        .card-body {
            padding: 20px;
            text-align: center;
        }

        .card-title {
            font-size: 22px;
            color: #fff;
            margin-bottom: 8px;
        }

        .card-price {
            font-size: 19px;
            color: var(--gold-primary);
            font-weight: bold;
        }

        .btn {
            display: inline-block;
            padding: 10px 22px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            border: none;
            cursor: pointer;
            transition: background 0.3s, transform 0.2s;
        }

        .btn-gold {
            background: linear-gradient(45deg, #b87333, #d4af37);
            color: #121316;
        }

        .btn-gold:hover {
            background: linear-gradient(45deg, #d4af37, #f3e5ab);
            transform: translateY(-2px);
        }

        .btn-blue {
            background-color: #2563eb;
            color: #fff;
        }

        .btn-danger {
            background-color: #dc2626;
            color: #fff;
        }

        .field {
            margin-bottom: 18px;
            text-align: right;
        }

        .field label {
            display: block;
            margin-bottom: 6px;
            color: var(--text-muted);
        }

        .field input {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            background-color: rgba(255, 255, 255, 0.05);
            color: #fff;
        }

        form {
            max-width: 480px;
            margin: 40px auto;
            background-color: var(--bg-card);
            padding: 30px;
            border-radius: 14px;
            border: 1px solid rgba(212, 175, 55, 0.2);
        }
    </style>
</head>
<body>

    <header>
        <a href="/" class="brand-title">✨ متجر أم ليليان</a>
        <div class="nav-links">
            <a href="/">المعرض الرئيسي</a>
            {% if session.get('is_admin') %}
                <a href="/admin">لوحة التحكم ⚙️</a>
                <a href="/admin/change-password">تغيير الباسورد 🔑</a>
                <a href="/logout">خروج 🚪</a>
            {% else %}
                <a href="/login">دخول الأدمن 🔒</a>
            {% endif %}
        </div>
    </header>

    {% block content %}{% endblock %}

</body>
</html>
"""

# الصفحة الرئيسية للزبائن
@app.route('/')
def home():
    items = Item.query.all()
    content = """
    <div class="hero-banner">
        <h1>مرحباً بكم في متجر أم ليليان</h1>
        <p>أرقى التشكيلات الفاخرة المختارة بعناية لتناسب ذوقك الرفيع</p>
        <div class="search-box">
            <input type="text" placeholder="ابحثي عن قطعتك المفضلة...">
        </div>
    </div>

    <div class="container">
        {% if items %}
            <div class="grid">
                {% for item in items %}
                    <div class="card">
                        <div class="card-img-wrapper">
                            <img src="{{ item.image }}" alt="{{ item.name }}">
                        </div>
                        <div class="card-body">
                            <h3 class="card-title">{{ item.name }}</h3>
                            <div class="card-price">{{ item.price }} د.أ</div>
                        </div>
                    </div>
                {% endfor %}
            </div>
        {% else %}
            <p style="text-align: center; color: var(--text-muted); margin-top: 2rem;">
                لا توجد قطع معروضة حالياً، يمكنك إضافتها من لوحة التحكم.
            </p>
        {% endif %}
    </div>
    """
    return render_template_string(HTML_LAYOUT.replace("{% block content %}", content), items=items)# تسجيل دخول الأدمن
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        admin_pass = AdminSetting.query.filter_by(key='password').first()
        if admin_pass and password == admin_pass.value:
            session['is_admin'] = True
            return redirect(url_for('admin'))
        else:
            error = "!كلمة المرور غير صحيحة"

    content = f"""
    <h2 style="text-align: center; margin-bottom: 25px; font-size: 30px;">دخول لوحة التحكم</h2>
    <form method="POST">
        {'<p style="color: red; text-align: center; margin-bottom: 10px;">' + error + '</p>' if error else ''}
        <div class="field">
            <label>كلمة المرور</label>
            <input type="password" name="password" required>
        </div>
        <button type="submit" class="btn btn-gold" style="width: 100%; padding: 12px;">تسجيل الدخول</button>
        <div style="text-align: center; margin-top: 15px;">
            <a href="/forgot-password" style="color: var(--gold-primary); text-decoration: none; font-size: 14px;">نسيت كلمة المرور؟</a>
        </div>
    </form>
    """
    return render_template_string(HTML_LAYOUT.replace("{% block content %}{% endblock %}", content))

# صفحة نسيت كلمة المرور (إرسال الباسورد للإيميل)
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    msg = None
    error = None
    if request.method == 'POST':
        admin_pass = AdminSetting.query.filter_by(key='password').first()
        if admin_pass:
            try:
                # إرسال كلمة المرور الحالية عبر البريد الإلكتروني المبرمج
                msg_mail = Message('استعادة كلمة مرور لوحة التحكم - متجر أم ليليان',
                              recipients=[app.config['MAIL_USERNAME']])
                msg_mail.body = f"مرحباً بك، كلمة المرور الخاصة بلوحة التحكم هي: {admin_pass.value}"
                mail.send(msg_mail)
                msg = "تم إرسال كلمة المرور بنجاح إلى بريدك الإلكتروني المعتمد!"
            except Exception as e:
                error = f"حدث خطأ أثناء إرسال البريد: تأكد من إعدادات البريد الصحيحة."

    content = f"""
    <h2 style="text-align: center; margin-bottom: 25px; font-size: 30px;">استعادة كلمة المرور</h2>
    <form method="POST">
        {'<p style="color: green; text-align: center; margin-bottom: 15px;">' + msg + '</p>' if msg else ''}
        {'<p style="color: red; text-align: center; margin-bottom: 15px;">' + error + '</p>' if error else ''}
        <p style="color: var(--text-muted); text-align: center; margin-bottom: 20px; font-size: 14px;">
            اضغط على الزر أدناه ليتم إرسال كلمة المرور الحالية فوراً إلى بريدك الإلكتروني المسجل.
        </p>
        <button type="submit" class="btn btn-gold" style="width: 100%; padding: 12px;">إرسال كلمة المرور إلى إيميلي</button>
        <div style="text-align: center; margin-top: 15px;">
            <a href="/login" style="color: var(--text-light); text-decoration: none; font-size: 14px;">العودة لتسجيل الدخول</a>
        </div>
    </form>
    """
    return render_template_string(HTML_LAYOUT.replace("{% block content %}{% endblock %}", content))

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('home'))

# تغيير كلمة المرور للأدمن
@app.route('/admin/change-password', methods=['GET', 'POST'])
def change_password():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    msg = None
    error = None
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        
        admin_pass = AdminSetting.query.filter_by(key='password').first()
        
        if admin_pass and old_password == admin_pass.value:
            admin_pass.value = new_password
            db.session.commit()
            msg = "تم تغيير كلمة المرور بنجاح!"
        else:
            error = "كلمة المرور الحالية غير صحيحة!"

    content = f"""
    <h2 style="text-align: center; margin-bottom: 25px; font-size: 30px;">تغيير كلمة المرور</h2>
    <form method="POST">
        {'<p style="color: green; text-align: center; margin-bottom: 10px;">' + msg + '</p>' if msg else ''}
        {'<p style="color: red; text-align: center; margin-bottom: 10px;">' + error + '</p>' if error else ''}
        <div class="field">
            <label>كلمة المرور الحالية</label>
            <input type="password" name="old_password" required>
        </div>
        <div class="field">
            <label>كلمة المرور الجديدة</label>
            <input type="password" name="new_password" required>
        </div>
        <button type="submit" class="btn btn-gold" style="width: 100%; padding: 12px;">حفظ كلمة المرور الجديدة</button>
    </form>
    """
    return render_template_string(HTML_LAYOUT.replace("{% block content %}{% endblock %}", content))

# لوحة تحكم الأدمن (عرض وإضافة)
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        file = request.files.get('image')

        if file:
            upload_result = cloudinary.uploader.upload(file)
            image_url = upload_result['secure_url']

            new_item = Item(name=name, price=price, image=image_url)
            db.session.add(new_item)
            db.session.commit()
            return redirect(url_for('admin'))

    items = Item.query.all()
    content = """
    <div class="container">
        <h2 style="text-align: center; margin: 20px 0; font-size: 32px;">إدارة المعرض</h2>
        
        <form method="POST" enctype="multipart/form-data">
            <h3 style="margin-bottom: 15px; text-align: center; color: var(--gold-primary);">إضافة قطعة جديدة</h3>
            <div class="field">
                <label>اسم القطعة</label>
                <input type="text" name="name" placeholder="مثال: طقم ذهب عيار 21" required>
            </div>
            <div class="field">
                <label>السعر</label>
                <input type="text" name="price" placeholder="مثال: 75 دينار" required>
            </div>
            <div class="field">
                <label>صورة القطعة</label>
                <input type="file" name="image" accept="image/*" required>
            </div>
            <button type="submit" class="btn btn-gold" style="width: 100%; padding: 12px;">نشر في المعرض</button>
        </form>

        <h3 style="margin-top: 40px; margin-bottom: 20px; font-size: 26px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">القطع الحالية:</h3>
        <div class="grid">
            {% for item in items %}
                <div class="card">
                    <div class="card-img-wrapper">
                        <img src="{{ item.image }}" alt="{{ item.name }}">
                    </div>
                    <div class="card-body">
                        <h3 class="card-title">{{ item.name }}</h3>
                        <div class="card-price">{{ item.price }}</div>
                        <div style="margin-top: 15px; display: flex; justify-content: space-around;">
                            <a href="/admin/edit/{{ item.id }}" class="btn btn-blue">تعديل</a>
                            <a href="/admin/delete/{{ item.id }}" class="btn btn-danger" onclick="return confirm('هل أنت تأكد من الحذف؟')">حذف</a>
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>
    </div>
    """
    return render_template_string(HTML_LAYOUT.replace("{% block content %}{% endblock %}", content), items=items)

# تعديل قطعة
@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
def edit_item(id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    item = Item.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.price = request.form['price']
        file = request.files.get('image')
        
        if file:
            upload_result = cloudinary.uploader.upload(file)
            item.image = upload_result['secure_url']
            
        db.session.commit()
        return redirect(url_for('admin'))

    content = """
    <h2 style="text-align: center; margin-top: 30px; font-size: 30px;">تعديل بيانات القطعة</h2>
    <form method="POST" enctype="multipart/form-data">
        <div class="field">
            <label>اسم القطعة</label>
            <input type="text" name="name" value="{{ item.name }}" required>
        </div>
        <div class="field">
            <label>السعر</label>
            <input type="text" name="price" value="{{ item.price }}" required>
        </div>
        <div class="field">
            <label>تغيير الصورة (اختياري)</label>
            <input type="file" name="image" accept="image/*">
        </div>
        <button type="submit" class="btn btn-blue" style="width: 100%; padding: 12px;">تحديث القطعة</button>
    </form>
    """
    return render_template_string(HTML_LAYOUT.replace("{% block content %}{% endblock %}", content), item=item)

# حذف قطعة
@app.route('/admin/delete/<int:id>')
def delete_item(id):
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)