from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Client, Tour, Route
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tours.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

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
        client.name = request.form['name']
        client.phone = request.form['phone']
        client.email = request.form['email']
        
        db.session.commit()
        flash('Данные клиента обновлены', 'success')
        return redirect(url_for('clients_list'))
    
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
    
    if request.method == 'POST':
        tour.route_id = request.form['route_id']
        tour.client_id = request.form['client_id']
        tour.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        tour.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        tour.status = request.form['status']
        
        db.session.commit()
        flash('Данные тура обновлены', 'success')
        return redirect(url_for('tours_list'))
    
    routes = Route.query.all()
    clients = Client.query.all()
    return render_template('tours/edit.html', tour=tour, routes=routes, clients=clients)

@app.route('/tours/delete/<int:id>')
def delete_tour(id):
    tour = Tour.query.get_or_404(id)
    db.session.delete(tour)
    db.session.commit()
    
    flash('Тур удален', 'success')
    return redirect(url_for('tours_list'))

if __name__ == '__main__':
    app.run(debug=True)