from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename  
from models import db, Client, Tour, Route
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tours.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'
# Конфигурация загрузки файлов
# Конфигурация загрузки файлов
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['CLIENT_PASSPORT_FOLDER'] = 'passports'
app.config['CLIENT_PHOTOS_FOLDER'] = 'profile_photos'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'pdf'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Создаем папки для загрузок
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], app.config['CLIENT_PASSPORT_FOLDER']), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], app.config['CLIENT_PHOTOS_FOLDER']), exist_ok=True)

db.init_app(app)

# Создаем таблицы при первом запуске
with app.app_context():
    db.create_all()

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Клиенты
@app.route('/clients')
def clients_list():
    clients = Client.query.all()
    return render_template('clients/list.html', clients=clients)

@app.route('/clients/add', methods=['GET', 'POST'])

def add_client():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        
        client = Client(name=name, phone=phone, email=email)
        db.session.add(client)
        db.session.commit()
        
        flash('Клиент успешно добавлен', 'success')
        return redirect(url_for('clients_list'))
    
    return render_template('clients/add.html')

@app.route('/clients/edit/<int:id>', methods=['GET', 'POST'])
def edit_client(id):
    client = Client.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Основные данные
            client.name = request.form['name']
            client.phone = request.form['phone']
            client.email = request.form.get('email', '')
            
            # Паспортные данные
            client.passport_series = request.form.get('passport_series')
            client.passport_number = request.form.get('passport_number')
            client.passport_issued_by = request.form.get('passport_issued_by')
            
            # Обработка даты выдачи паспорта
            if request.form.get('passport_issue_date'):
                client.passport_issue_date = datetime.strptime(
                    request.form['passport_issue_date'], '%Y-%m-%d').date()
            
            # Обработка скана паспорта
            if 'passport_image' in request.files:
                file = request.files['passport_image']
                if file.filename != '':
                    if not allowed_file(file.filename):
                        flash('Недопустимый формат файла паспорта. Разрешены: png, jpg, jpeg, pdf', 'danger')
                    else:
                        # Удаляем старый файл если он существует
                        if client.passport_image:
                            try:
                                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], client.passport_image))
                            except Exception as e:
                                print(f"Ошибка при удалении файла паспорта: {e}")
                        
                        # Сохраняем новый файл
                        ext = file.filename.rsplit('.', 1)[1].lower()
                        filename = secure_filename(f"passport_{client.id}_{int(datetime.now().timestamp())}.{ext}")
                        save_path = os.path.join(app.config['UPLOAD_FOLDER'], app.config['CLIENT_PASSPORT_FOLDER'], filename)
                        file.save(save_path)
                        client.passport_image = os.path.join(app.config['CLIENT_PASSPORT_FOLDER'], filename)
            
            # Обработка фото профиля
            if 'profile_image' in request.files:
                file = request.files['profile_image']
                if file.filename != '':
                    if not allowed_file(file.filename):
                        flash('Недопустимый формат фото. Разрешены: png, jpg, jpeg', 'danger')
                    else:
                        # Удаляем старый файл если он существует
                        if client.profile_image:
                            try:
                                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], client.profile_image))
                            except Exception as e:
                                print(f"Ошибка при удалении фото профиля: {e}")
                        
                        # Сохраняем новый файл
                        ext = file.filename.rsplit('.', 1)[1].lower()
                        filename = secure_filename(f"profile_{client.id}")
                        save_path = os.path.join(app.config['UPLOAD_FOLDER'], app.config['CLIENT_PHOTOS_FOLDER'], filename)
                        file.save(save_path)
                        client.profile_image = os.path.join(app.config['CLIENT_PHOTOS_FOLDER'], filename)
            
            # Удаление фото профиля
            if request.form.get('remove_profile_image'):
                if client.profile_image:
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], client.profile_image))
                        client.profile_image = None
                    except Exception as e:
                        print(f"Ошибка при удалении фото профиля: {e}")
            
            db.session.commit()
            flash('Данные клиента успешно обновлены', 'success')
            return redirect(url_for('clients_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Произошла ошибка при обновлении данных: {str(e)}', 'danger')
    
    return render_template('clients/edit.html', client=client)

@app.route('/clients/delete/<int:id>')
def delete_client(id):
    client = Client.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()
    
    flash('Клиент удален', 'success')
    return redirect(url_for('clients_list'))

# Маршруты
@app.route('/routes')
def routes_list():
    routes = Route.query.all()
    return render_template('routes/list.html', routes=routes)

@app.route('/routes/add', methods=['GET', 'POST'])
def add_route():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        duration = request.form['duration']
        price = request.form['price']
        
        route = Route(name=name, description=description, duration=duration, price=price)
        db.session.add(route)
        db.session.commit()
        
        flash('Маршрут успешно добавлен', 'success')
        return redirect(url_for('routes_list'))
    
    return render_template('routes/add.html')

@app.route('/routes/edit/<int:id>', methods=['GET', 'POST'])
def edit_route(id):
    route = Route.query.get_or_404(id)
    
    if request.method == 'POST':
        route.name = request.form['name']
        route.description = request.form['description']
        route.duration = request.form['duration']
        route.price = request.form['price']
        
        db.session.commit()
        flash('Данные маршрута обновлены', 'success')
        return redirect(url_for('routes_list'))
    
    return render_template('routes/edit.html', route=route)

@app.route('/routes/delete/<int:id>')
def delete_route(id):
    route = Route.query.get_or_404(id)
    db.session.delete(route)
    db.session.commit()
    
    flash('Маршрут удален', 'success')
    return redirect(url_for('routes_list'))

# Туры
@app.route('/tours')
def tours_list():
    tours = Tour.query.join(Route).join(Client).all()
    return render_template('tours/list.html', tours=tours)

@app.route('/tours/add', methods=['GET', 'POST'])
def add_tour():
    if request.method == 'POST':
        route_id = request.form['route_id']
        client_id = request.form['client_id']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        status = request.form['status']
        
        tour = Tour(
            route_id=route_id,
            client_id=client_id,
            start_date=start_date,
            end_date=end_date,
            status=status
        )
        db.session.add(tour)
        db.session.commit()
        
        flash('Тур успешно добавлен', 'success')
        return redirect(url_for('tours_list'))
    
    routes = Route.query.all()
    clients = Client.query.all()
    return render_template('tours/add.html', routes=routes, clients=clients)


@app.route('/tours/edit/<int:id>', methods=['GET', 'POST'])
def edit_tour(id):
    tour = Tour.query.get_or_404(id)
    routes = Route.query.all()
    clients = Client.query.all()
    
    if request.method == 'POST':
        tour.route_id = request.form['route_id']
        tour.client_id = request.form['client_id']
        tour.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        tour.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        tour.status = request.form['status']
        db.session.commit()
        flash('Тур обновлен', 'success')
        return redirect(url_for('tours_list'))
    
    return render_template('tours/edit.html', 
                         tour=tour, 
                         routes=routes, 
                         clients=clients)

@app.route('/tours/delete/<int:id>')
def delete_tour(id):
    tour = Tour.query.get_or_404(id)
    db.session.delete(tour)
    db.session.commit()
    
    flash('Тур удален', 'success')
    return redirect(url_for('tours_list'))


def allowed_file(filename):
    """Проверяет расширение файла"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def check_file_size(file):
    """Проверяет размер файла"""
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    return file_size <= app.config['MAX_CONTENT_LENGTH']

if __name__ == '__main__':
    app.run(debug=True)