import os
from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'um_lilian_jewelry_secret_2026'

# 🔑 كلمة المرور الخاصة بالأدمن
ADMIN_PASSWORD = 'admin123password'

# 📱 رقم الواتساب الخاص باستقبال الطلبات (يمكنك تغييره هنا بكتابة الرقم مع الرمز الدولي مثلاً: 9627XXXXXXXX)
WHATSAPP_NUMBER = '962797174200'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(255), nullable=False)

with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 👑 الهيكل الرئيسي والتصميم العصري الفاخر
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>متجر أم ليليان | Um Lilian Jewelry</title>
    <link href="https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --gold-primary: #d4af37;
            --gold-gradient: linear-gradient(135deg, #bf953f, #fcf6ba, #b38728, #fbf5b7, #aa771c);
            --gold-hover: #c59b27;
            --dark-bg: #0f0f11;
            --card-bg: #ffffff;
            --body-bg: #f9f8f6;
            --text-main: #2b2b2b;
            --text-gold: #997424;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Tajawal', sans-serif; background: var(--body-bg); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; }
        
        /* الهيدر الفاخر */
        header { 
            background: var(--dark-bg); 
            padding: 18px 5%; 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            border-bottom: 2px solid var(--gold-primary);
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            position: sticky; top: 0; z-index: 100;
        }
        .brand-logo { 
            font-family: 'Amiri', serif;
            font-size: 26px; 
            font-weight: bold; 
            background: var(--gold-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-decoration: none; 
            display: flex; align-items: center; gap: 10px;
        }
        nav { display: flex; align-items: center; gap: 20px; }
        nav a { 
            color: #e0e0e0; 
            text-decoration: none; 
            font-size: 15px; 
            font-weight: 500; 
            transition: all 0.3s;
            display: flex; align-items: center; gap: 6px;
        }
        nav a:hover { color: var(--gold-primary); }
        .nav-btn-admin {
            border: 1px solid var(--gold-primary);
            padding: 6px 14px;
            border-radius: 20px;
        }

        /* المحتوى الرئيسي */
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; flex: 1; width: 100%; }
        
        /* بنر الترحيب */
        .hero-banner {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px 20px;
            background: #fff;
            border-radius: 16px;
            box-shadow: 0 4px 25px rgba(0,0,0,0.03);
            border: 1px solid #eae5db;
        }
        .hero-banner h1 { 
            font-family: 'Amiri', serif; 
            font-size: 38px; 
            color: #1a1a1a; 
            margin-bottom: 10px;
        }
        .hero-banner p { color: #666; font-size: 16px; max-width: 600px; margin: 0 auto 20px; }
        
        /* حقل البحث */
        .search-box {
            max-width: 450px;
            margin: 0 auto;
            position: relative;
        }
        .search-box input {
            width: 100%;
            padding: 12px 45px 12px 20px;
            border-radius: 30px;
            border: 1px solid #ddd;
            outline: none;
            font-size: 15px;
            transition: 0.3s;
        }
        .search-box input:focus { border-color: var(--gold-primary); box-shadow: 0 0 10px rgba(212,175,55,0.2); }
        .search-box i { position: absolute; right: 18px; top: 50%; transform: translateY(-50%); color: #888; }

        /* شبكة المنتجات */
        .grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); 
            gap: 30px; 
            margin-top: 30px; 
        }
        .card { 
            background: var(--card-bg); 
            border-radius: 14px; 
            overflow: hidden; 
            border: 1px solid #eee;
            box-shadow: 0 6px 18px rgba(0,0,0,0.04); 
            transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1);
            display: flex; flex-direction: column;
            position: relative;
        }
        .card:hover { 
            transform: translateY(-8px); 
            box-shadow: 0 14px 28px rgba(0,0,0,0.1); 
            border-color: rgba(212,175,55,0.4);
        }
        .img-container {
            width: 100%; height: 320px; overflow: hidden; position: relative; background: #fafafa; cursor: pointer;
        }
        .card img { 
            width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s ease; 
        }
        .card:hover img { transform: scale(1.06); }
        .card-info { padding: 20px; text-align: center; display: flex; flex-direction: column; flex: 1; justify-content: space-between; }
        .title { font-size: 18px; font-weight: 700; color: #222; margin-bottom: 8px; }
        .price-tag { 
            font-size: 20px; 
            font-weight: 800; 
            color: var(--text-gold); 
            margin-bottom: 15px; 
            font-family: 'Tajawal', sans-serif;
        }
        
        /* الأزرار */
        .btn { 
            padding: 11px 20px; 
            border-radius: 30px; 
            text-decoration: none; 
            font-weight: bold; 
            display: inline-flex; align-items: center; justify-content: center; gap: 8px;
            border: none; cursor: pointer; transition: 0.3s; font-size: 14px;
        }
        .btn-whatsapp { 
            background: #25D366; color: #fff; width: 100%;
        }
        .btn-whatsapp:hover { background: #1ebc57; box-shadow: 0 4px 12px rgba(37,211,102,0.3); }
        
        .btn-gold { background: var(--gold-primary); color: #fff; }
        .btn-gold:hover { background: var(--gold-hover); }
        .btn-danger { background: #e74c3c; color: #fff; }
        .btn-blue { background: #3498db; color: #fff; }

        /* نموذج الإدارة والجدول */
        table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 12px; overflow: hidden; margin-top: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        th, td { padding: 15px; text-align: center; border-bottom: 1px solid #eee; }
        th { background: var(--dark-bg); color: var(--gold-primary); font-weight: 600; }
        td img { width: 60px; height: 80px; object-fit: cover; border-radius: 6px; }
        
        form { background: #fff; padding: 35px; border-radius: 16px; max-width: 450px; margin: 0 auto; box-shadow: 0 6px 20px rgba(0,0,0,0.06); border: 1px solid #eee; }
        .field { margin-bottom: 22px; text-align: right; }
        .field label { display: block; margin-bottom: 8px; font-weight: 700; font-size: 14px; }
        .field input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; outline: none; transition: 0.3s; }
        .field input:focus { border-color: var(--gold-primary); }

        /* نافذة مكبّر الصور Modal */
        .modal {
            display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%;
            background-color: rgba(0,0,0,0.85); backdrop-filter: blur(5px); justify-content: center; align-items: center;
        }
        .modal img { max-width: 90%; max-height: 85vh; border-radius: 10px; border: 2px solid var(--gold-primary); }
        .close-modal { position: absolute; top: 20px; right: 35px; color: #fff; font-size: 40px; cursor: pointer; }

        footer { text-align: center; padding: 25px; background: var(--dark-bg); color: #888; border-top: 1px solid #222; font-size: 14px; }
    </style>
</head>
<body>
    <header>
        <a href="/" class="brand-logo">💎 متجر أم ليليان</a>
        <nav>
            <a href="/"><i class="fa-solid fa-gem"></i> المعرض الرئيسي</a>
            {% if session.get('is_admin') %}
                <a href="/admin" class="nav-btn-admin"><i class="fa-solid fa-sliders"></i> لوحة الأدمن</a>
                <a href="/logout" style="color: #ff6b6b;"><i class="fa-solid fa-right-from-bracket"></i> خروج</a>
            {% else %}
                <a href="/login" class="nav-btn-admin"><i class="fa-solid fa-lock"></i> دخول الأدمن</a>
            {% endif %}
        </nav>
    </header>

    <div class="container">
        {% block content %}{% endblock %}
    </div>

    <!-- نافذة تكبير الصور -->
    <div id="imageModal" class="modal" onclick="closeModal()">
        <span class="close-modal">&times;</span>
        <img id="modalImg" src="">
    </div>

    <footer>
        جميع الحقوق محفوظة © 2026 - متجر أم ليليان ✨
    </footer>

    <script>
        function openModal(src) {
            document.getElementById('modalImg').src = src;
            document.getElementById('imageModal').style.display = 'flex';
        }
        function closeModal() {
            document.getElementById('imageModal').style.display = 'none';
        }
        function filterItems() {
            let input = document.getElementById('searchInput').value.toLowerCase();
            let cards = document.getElementsByClassName('card');
            for (let i = 0; i < cards.length; i++) {
                let title = cards[i].getElementsByClassName('title')[0].innerText.toLowerCase();
                if (title.includes(input)) {
                    cards[i].style.display = "";
                } else {
                    cards[i].style.display = "none";
                }
            }
        }
    </script>
</body>
</html>
"""

# المعرض الرئيسي للزبائن
@app.route('/')
def index():
    items = Item.query.all()
    content = f"""
        <div class="hero-banner">
            <h1>مرحباً بكم في متجر أم ليليان</h1>
            <p>أرقى التشكيلات الفاخرة مختارة بعناية لتناسب ذوقك الرفيع</p>
            <div class="search-box">
                <i class="fa-solid fa-magnifying-glass"></i>
                <input type="text" id="searchInput" onkeyup="filterItems()" placeholder="ابحثي عن قطعتك المفضلة...">
            </div>
        </div>

        <div class="grid">
            {{% for item in items %}}
            <div class="card">
                <div class="img-container" onclick="openModal('{{{{ url_for('static', filename='uploads/' + item.image) }}}}')">
                    <img src="{{{{ url_for('static', filename='uploads/' + item.image) }}}}" alt="{{{{ item.name }}}}">
                </div>
                <div class="card-info">
                    <div>
                        <div class="title">{{{{ item.name }}}}</div>
                        <div class="price-tag">{{{{ item.price }}}}</div>
                    </div>
                    <a href="https://wa.me/{WHATSAPP_NUMBER}?text=مرحباً%20متجر%20أم%20ليليان،%20أرغب%20في%20الاستفسار%20عن%20قطعة:%20{{{{ item.name }}}}%20بسعر%20{{{{ item.price }}}}" 
                       target="_blank" class="btn btn-whatsapp">
                       <i class="fa-brands fa-whatsapp" style="font-size:18px;"></i> اطلبي عبر الواتساب
                    </a>
                </div>
            </div>
            {{% else %}}
            <p style="grid-column: 1/-1; text-align: center; color: #888; padding: 40px;">لا توجد قطع معروضة حالياً. يمكنك إضافتها من لوحة التحكم.</p>
            {{% endfor %}}
        </div>
    """
    return render_template_string(HTML_LAYOUT.replace("{% block content %}{% endblock %}", content), items=items)

# صفحة تسجيل دخول الأدمن
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('admin'))
        else:
            error = "كلمة المرور غير صحيحة!"

    content = f"""
        <h2 style="text-align: center; margin-bottom: 25px; font-family: 'Amiri', serif; font-size: 30px;">دخول لوحة التحكم</h2>
        <form method="POST">
            {"<div style='background:#f8d7da; color:#721c24; padding:10px; border-radius:8px; margin-bottom:15px; text-align:center;'>" + error + "</div>" if error else ""}
            <div class="field">
                <label>كلمة مرور الأدمن</label>
                <input type="password" name="password" placeholder="أدخلي كلمة المرور" required>
            </div>
            <button type="submit" class="btn btn-gold" style="width: 100%;">تسجيل الدخول</button>
        </form>
    """
    return render_template_string(HTML_LAYOUT.replace("{% block content %}{% endblock %}", content))

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

# لوحة تحكم الأدمن
@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    items = Item.query.all()
    content = """
        <h2 style="text-align: center; margin-bottom: 20px; font-family: 'Amiri', serif; font-size: 32px;">لوحة إشراف متجر أم ليليان</h2>
        <div style="text-align: center; margin-bottom: 30px;">
            <a href="/admin/add" class="btn btn-gold" style="padding: 12px 25px; font-size: 16px;">
                <i class="fa-solid fa-plus"></i> إضافة قطعة جديدة
            </a>
        </div>
        <table>
            <thead>
                <tr>
                    <th>الصورة</th>
                    <th>اسم القطعة</th>
                    <th>السعر</th>
                    <th>الإجراءات</th>
                </tr>
            </thead>
            <tbody>
                {% for item in items %}
                <tr>
                    <td><img src="{{ url_for('static', filename='uploads/' + item.image) }}"></td>
                    <td><b>{{ item.name }}</b></td>
                    <td style="color: var(--text-gold); font-weight: bold;">{{ item.price }}</td>
                    <td>
                        <a href="/admin/edit/{{ item.id }}" class="btn btn-blue" style="padding: 6px 12px; font-size: 12px;"><i class="fa-solid fa-pen"></i> تعديل</a>
                        <a href="/admin/delete/{{ item.id }}" class="btn btn-danger" style="padding: 6px 12px; font-size: 12px;" onclick="return confirm('هل أنتِ تأكدة من حذف هذه القطعة؟')"><i class="fa-solid fa-trash"></i> حذف</a>
                    </td>
                </tr>
                {% else %}
                <tr><td colspan="4" style="padding: 30px; color: #777;">قاعدة البيانات فارغة حالياً. اضغطي على زر الإضافة أعلاه لبدء إضافة المعروضات.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    """
    return render_template_string(HTML_LAYOUT.replace("{% block content %}{% endblock %}", content), items=items)

# إضافة قطعة جديدة
@app.route('/admin/add', methods=['GET', 'POST'])
def add_item():
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        file = request.files.get('image')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            new_item = Item(name=name, price=price, image=filename)
            db.session.add(new_item)
            db.session.commit()
            return redirect(url_for('admin'))

    content = """
        <h2 style="text-align: center; margin-bottom: 25px; font-family: 'Amiri', serif; font-size: 30px;">إضافة قطعة جديدة</h2>
        <form method="POST" enctype="multipart/form-data">
            <div class="field">
                <label>اسم القطعة</label>
                <input type="text" name="name" placeholder="مثال: سنسال الأونصة الملكي" required>
            </div>
            <div class="field">
                <label>السعر</label>
                <input type="text" name="price" placeholder="مثال: 75 دينار" required>
            </div>
            <div class="field">
                <label>صورة القطعة الأصلية</label>
                <input type="file" name="image" accept="image/*" required>
            </div>
            <button type="submit" class="btn btn-gold" style="width: 100%; padding: 12px;">نشر في المعرض</button>
        </form>
    """
    return render_template_string(HTML_LAYOUT.replace("{% block content %}{% endblock %}", content))

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
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            item.image = filename
        db.session.commit()
        return redirect(url_for('admin'))

    content = """
        <h2 style="text-align: center; margin-bottom: 25px; font-family: 'Amiri', serif; font-size: 30px;">تعديل بيانات القطعة</h2>
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
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], item.image)
    if os.path.exists(img_path):
        os.remove(img_path)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)