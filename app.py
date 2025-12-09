from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import os
import json
from functools import wraps
from datetime import datetime
from werkzeug.utils import secure_filename
import pandas as pd  # <-- استدعاء مكتبة pandas هنا

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def load_users():
    with open('users.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_data():
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_data(data):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']
        for user in users:
            if user['username'] == username and user['password'] == password:
                session['username'] = username
                session['role'] = user['role']
                if user['role'] == 'employee':
                    return redirect(url_for('employee_home'))
                else:
                    return redirect(url_for('view_requests'))
        flash("❌ اسم المستخدم أو كلمة المرور غير صحيحة.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/employee')
@login_required
def employee_home():
    return render_template('employee.html', username=session['username'])

@app.route('/submit', methods=['GET', 'POST'])
@login_required
def submit_request():
    if session['role'] != 'employee':
        return "Unauthorized", 403

    if request.method == 'POST':
        data = load_data()
        description = request.form['description']
        status = request.form['status']
        date = datetime.now().strftime('%Y-%m-%d %H:%M')
        attachment = None

        file = request.files.get('attachment')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            file.save(filepath)
            attachment = filename

        task = {
            "employee": session['username'],
            "description": description,
            "status": status,
            "date": date,
            "attachment": attachment,
            "notes": "",
            "rating": ""
        }

        data.append(task)
        save_data(data)
        flash("✅ تم إرسال المهمة بنجاح")
        return redirect(url_for('employee_home'))

    return render_template('submit.html')

@app.route('/requests')
@login_required
def view_requests():
    if session['role'] != 'manager':
        return "Unauthorized", 403
    data = load_data()
    return render_template('requests.html', requests=data)

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    data = load_data()
    if task_id < 0 or task_id >= len(data):
        return "المهمة غير موجودة", 404

    task = data[task_id]

    if request.method == 'POST':
        task['description'] = request.form['description']
        task['status'] = request.form['status']
        task['notes'] = request.form.get('notes', '')
        save_data(data)
        flash("✅ تم تعديل المهمة بنجاح")
        return redirect(url_for('view_requests'))
    return render_template('edit.html', task=task, task_id=task_id)

@app.route('/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    data = load_data()
    if task_id < 0 or task_id >= len(data):
        return "المهمة غير موجودة", 404

    data.pop(task_id)
    save_data(data)
    flash("🗑 تم حذف المهمة")
    return redirect(url_for('view_requests'))

@app.route('/submit_ratings', methods=['POST'])
@login_required
def submit_ratings():
    if session['role'] != 'manager':
        return "Unauthorized", 403

    data = load_data()
    for i, task in enumerate(data):
        rating = request.form.get(f'ratings_{i}')
        if rating:
            task['rating'] = rating

    save_data(data)
    flash("✅ تم حفظ التقييمات بنجاح")
    return redirect(url_for('view_requests'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/employee/tasks')
@login_required
def employee_ts():
    if session['role'] != 'employee':
        return "Unauthorized", 403
    username = session['username']
    data = load_data()
    tasks = [task for task in data if task['employee'] == username]
    return render_template('employee_ts.html', tasks=tasks)

@app.route('/rate')
@login_required
def rate_page():
    return render_template('rate.html')


# -------- الجزء الجديد: تصدير المهام إلى Excel -----------

@app.route('/export')
@login_required
def export_to_excel():
    if session.get('role') != 'manager':
        return "Unauthorized", 403

    data = load_data()

    # تحويل القائمة لقالب DataFrame
    df = pd.DataFrame(data)

    # مسار حفظ الملف داخل مجلد static
    export_folder = 'static'
    os.makedirs(export_folder, exist_ok=True)
    file_path = os.path.join(export_folder, 'engazat.xlsx')

    # حفظ الملف Excel
    df.to_excel(file_path, index=False)

    # إرسال الملف للتحميل مباشرة
    return send_from_directory(export_folder, 'engazat.xlsx', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)