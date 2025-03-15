from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Inicialización de la aplicación y la base de datos
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recetas.db'  # Nombre de la base de datos
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Inicializar el gestor de inicio de sesión
login_manager = LoginManager()
login_manager.init_app(app)

# Definir el modelo de base de datos para los folios
class Folio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    estado = db.Column(db.String(20), nullable=False)  # Estado del folio (PARCIAL, COMPLETA, INCOMPLETA)
    medico = db.Column(db.String(2), nullable=False)  # Iniciales del médico (T, E, P, A)
    fecha_ocupacion = db.Column(db.String(50), nullable=False)  # Fecha en que se ocupó el folio
    usuario_ocupa = db.Column(db.String(100), nullable=False)  # Usuario que utilizó el folio

# Definir el modelo de base de datos para los usuarios (para autenticación)
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Función para cargar el usuario
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para el login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = Usuario.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas', 'danger')
    
    return render_template('login.html')

# Ruta para el panel de control
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Ruta para agregar un nuevo folio
@app.route('/agregar_folio', methods=['GET', 'POST'])
@login_required
def agregar_folio():
    if request.method == 'POST':
        estado = request.form['estado']
        medico = request.form['medico']
        fecha_ocupacion = request.form['fecha_ocupacion']
        usuario_ocupa = current_user.username

        # Verificar si el folio ya existe
        if Folio.query.filter_by(estado=estado, medico=medico, fecha_ocupacion=fecha_ocupacion).first():
            flash('Este folio ya ha sido registrado', 'danger')
        else:
            nuevo_folio = Folio(estado=estado, medico=medico, fecha_ocupacion=fecha_ocupacion, usuario_ocupa=usuario_ocupa)
            db.session.add(nuevo_folio)
            db.session.commit()
            flash('Folio agregado exitosamente', 'success')
    
    return render_template('agregar_folio.html')

# Ruta para cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Iniciar el servidor
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
