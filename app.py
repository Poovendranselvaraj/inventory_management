from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)

# Models
class Product(db.Model):
    product_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

class Location(db.Model):
    location_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class ProductMovement(db.Model):
    movement_id = db.Column(db.String(50), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    from_location = db.Column(db.String(50), db.ForeignKey('location.location_id'))
    to_location = db.Column(db.String(50), db.ForeignKey('location.location_id'))
    product_id = db.Column(db.String(50), db.ForeignKey('product.product_id'))
    qty = db.Column(db.Integer, nullable=False)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Product routes
@app.route('/products')
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product = Product(
            product_id=request.form['product_id'],
            name=request.form['name'],
            description=request.form['description']
        )
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('products'))
    return render_template('add_product.html')

@app.route('/products/edit/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get(product_id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        db.session.commit()
        return redirect(url_for('products'))
    return render_template('edit_product.html', product=product)

# Location routes
@app.route('/locations')
def locations():
    locations = Location.query.all()
    return render_template('locations.html', locations=locations)

@app.route('/locations/add', methods=['GET', 'POST'])
def add_location():
    if request.method == 'POST':
        location = Location(
            location_id=request.form['location_id'],
            name=request.form['name']
        )
        db.session.add(location)
        db.session.commit()
        return redirect(url_for('locations'))
    return render_template('add_location.html')

@app.route('/locations/edit/<location_id>', methods=['GET', 'POST'])
def edit_location(location_id):
    location = Location.query.get(location_id)
    if request.method == 'POST':
        location.name = request.form['name']
        db.session.commit()
        return redirect(url_for('locations'))
    return render_template('edit_location.html', location=location)

# Product Movement routes
@app.route('/movements')
def movements():
    movements = ProductMovement.query.all()
    return render_template('movements.html', movements=movements)

@app.route('/movements/add', methods=['GET', 'POST'])
def add_movement():
    if request.method == 'POST':
        movement = ProductMovement(
            movement_id=request.form['movement_id'],
            from_location=request.form['from_location'] or None,
            to_location=request.form['to_location'] or None,
            product_id=request.form['product_id'],
            qty=int(request.form['qty'])
        )
        db.session.add(movement)
        db.session.commit()
        return redirect(url_for('movements'))
    products = Product.query.all()
    locations = Location.query.all()
    return render_template('add_movement.html', products=products, locations=locations)

@app.route('/movements/edit/<movement_id>', methods=['GET', 'POST'])
def edit_movement(movement_id):
    movement = ProductMovement.query.get(movement_id)
    if request.method == 'POST':
        movement.from_location = request.form['from_location'] or None
        movement.to_location = request.form['to_location'] or None
        movement.product_id = request.form['product_id']
        movement.qty = int(request.form['qty'])
        db.session.commit()
        return redirect(url_for('movements'))
    products = Product.query.all()
    locations = Location.query.all()
    return render_template('edit_movement.html', movement=movement, products=products, locations=locations)

# Report route
@app.route('/report')
def report():
    products = Product.query.all()
    locations = Location.query.all()
    balance = {}
    
    for product in products:
        balance[product.product_id] = {}
        for location in locations:
            balance[product.product_id][location.location_id] = 0

    movements = ProductMovement.query.all()
    for movement in movements:
        if movement.from_location:
            balance[movement.product_id][movement.from_location] -= movement.qty
        if movement.to_location:
            balance[movement.product_id][movement.to_location] += movement.qty

    return render_template('report.html', balance=balance, products=products, locations=locations)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)