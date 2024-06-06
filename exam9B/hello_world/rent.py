from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
db = SQLAlchemy(app)

class User(db.Model):
    id_user = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    # Añade otros campos según sea necesario

class Book(db.Model):
    id_book = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    # Añade otros campos según sea necesario

class Rent(db.Model):
    id_rents = db.Column(db.Integer, primary_key=True)
    initial_date = db.Column(db.Date, nullable=False)
    final_date = db.Column(db.Date, nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id_user'), nullable=False)
    id_book = db.Column(db.Integer, db.ForeignKey('book.id_book'), nullable=False)
    status = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref='rents')
    book = db.relationship('Book', backref='rents')

def rent_book():
    data = request.json
    user_id = data.get('user_id')
    book_id = data.get('book_id')

    # Verificar si el usuario ya tiene el libro rentado
    existing_rent = Rent.query.filter_by(id_user=user_id, id_book=book_id).first()
    if existing_rent:
        return jsonify({'message': 'El usuario ya tiene este libro rentado'}), 400

    # Verificar si el usuario ya tiene 2 libros rentados
    rent_count = Rent.query.filter_by(id_user=user_id).count()
    if rent_count >= 2:
        return jsonify({'message': 'El usuario no puede rentar más de 2 libros'}), 400

    # Crear la renta
    today = datetime.today().date()
    end_date = today + timedelta(days=2)  # 2 días de renta
    rent = Rent(initial_date=today, final_date=end_date, id_user=user_id, id_book=book_id)
    db.session.add(rent)
    db.session.commit()

    return jsonify({'message': 'Renta guardada correctamente'}), 200

if __name__ == '__main__':
    app.run(debug=True)
