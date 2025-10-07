from flask import Blueprint, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from config.mysqlconnection import connectToMySQL
import re

usuarios_bp = Blueprint('usuarios', __name__)
DB = 'certificacion'
EMAIL_RE = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

def validar_registro(form):
    errors = []
    if len(form.get('nombre','').strip()) < 2:
        errors.append('Nombre debe tener al menos 2 caracteres')
    if len(form.get('apellido','').strip()) < 2:
        errors.append('Apellido debe tener al menos 2 caracteres')
    email = form.get('email','').strip()
    if not EMAIL_RE.match(email):
        errors.append('Email inválido')
    if len(form.get('password','')) < 6:
        errors.append('Contraseña debe tener al menos 6 caracteres')
    if form.get('password') != form.get('confirm'):
        errors.append('Contraseñas no coinciden')
    mysql = connectToMySQL(DB)
    existing = mysql.query_db('SELECT id FROM users WHERE email=%(email)s', {'email': email})
    if existing:
        errors.append('Email ya registrado')
    return errors


@usuarios_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    errors = validar_registro(request.form)
    if errors:
        for e in errors:
            flash(e, 'error')
        return render_template('register.html')
    pw_hash = generate_password_hash(request.form['password'])
    mysql = connectToMySQL(DB)
    query = 'INSERT INTO users (nombre, apellido, email, password) VALUES (%(nombre)s, %(apellido)s, %(email)s, %(password)s)'
    data = {
        'nombre': request.form['nombre'].strip(),
        'apellido': request.form['apellido'].strip(),
        'email': request.form['email'].strip(),
        'password': pw_hash
    }
    user_id = mysql.query_db(query, data)
    session['user_id'] = user_id
    session['user_name'] = data['nombre']
    flash('Registro exitoso', 'success')
    return redirect('/')


@usuarios_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    email = request.form['email'].strip()
    password = request.form['password']
    mysql = connectToMySQL(DB)
    query = 'SELECT * FROM users WHERE email=%(email)s'
    user = mysql.query_db(query, {'email': email})
    if not user:
        flash('Credenciales inválidas', 'error')
        return render_template('login.html')
    user = user[0]
    if not check_password_hash(user['password'], password):
        flash('Credenciales inválidas', 'error')
        return render_template('login.html')
    session['user_id'] = user['id']
    session['user_name'] = user['nombre']
    return redirect('/')


@usuarios_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
