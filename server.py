from flask import Flask
from config.mysqlconnection import connectToMySQL

app = Flask(__name__)
app.secret_key = 'replace-this-secret'
DB = 'certificacion'

# register blueprints
from controllers.usuarios import usuarios_bp
from controllers.asesorias import asesorias_bp
app.register_blueprint(usuarios_bp)
app.register_blueprint(asesorias_bp)


# debug helpers
@app.route('/debug/usuarios')
def debug_usuarios():
    if not app.debug:
        return 'Not available', 404
    mysql = connectToMySQL(DB)
    users = mysql.query_db('SELECT id, nombre, apellido, email FROM users')
    rows = ['<tr><th>id</th><th>nombre</th><th>apellido</th><th>email</th></tr>']
    for u in users:
        rows.append(f"<tr><td>{u.get('id')}</td><td>{u.get('nombre')}</td><td>{u.get('apellido')}</td><td>{u.get('email')}</td></tr>")
    html = '<h2>Usuarios en la BD</h2><table border="1">' + '\n'.join(rows) + '</table>'
    return html

@app.route('/debug/tutores')
def debug_tutores():
    if not app.debug:
        return 'Not available', 404
    mysql = connectToMySQL(DB)
    tutors = mysql.query_db('SELECT id, nombre, apellido, email FROM tutors')
    rows = ['<tr><th>id</th><th>nombre</th><th>apellido</th><th>email</th></tr>']
    for t in tutors:
        rows.append(f"<tr><td>{t.get('id')}</td><td>{t.get('nombre')}</td><td>{t.get('apellido')}</td><td>{t.get('email')}</td></tr>")
    html = '<h2>Tutores en la BD</h2><table border="1">' + '\n'.join(rows) + '</table>'
    return html

@app.route('/debug/asesorias')
def debug_asesorias():
    if not app.debug:
        return 'Not available', 404
    mysql = connectToMySQL(DB)
    ases = mysql.query_db('SELECT * FROM asesorias')
    rows = ['<tr><th>id</th><th>tema</th><th>fecha</th><th>usuario_id</th><th>tutor_id</th></tr>']
    for a in ases:
        rows.append(f"<tr><td>{a.get('id')}</td><td>{a.get('tema')}</td><td>{a.get('fecha')}</td><td>{a.get('usuario_id')}</td><td>{a.get('tutor_id')}</td></tr>")
    html = '<h2>Asesorias</h2><table border="1">' + '\n'.join(rows) + '</table>'
    return html

# Ensure tutors table exists and is seeded at startup (best-effort)
def ensure_tutors_seeded():
	try:
		mysql = connectToMySQL(DB)
		# create tutors table if it doesn't exist
		mysql.query_db('''
		CREATE TABLE IF NOT EXISTS tutors (
			id INT AUTO_INCREMENT PRIMARY KEY,
			nombre VARCHAR(100) NOT NULL,
			apellido VARCHAR(100),
			email VARCHAR(255) NOT NULL UNIQUE,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
		''')
		# check count
		res = mysql.query_db('SELECT COUNT(*) AS c FROM tutors')
		count = res[0]['c'] if res else 0
		if count == 0:
			mysql.query_db("""
			INSERT IGNORE INTO tutors (nombre, apellido, email) VALUES
			  ('Liza','Molina','liza.molina@example.com'),
			  ('Bastian','Chavez','bastian.chavez@example.com'),
			  ('Fernando','Ojeada','fernando.ojeada@example.com'),
			  ('Carlos','Toro','carlos.toro@example.com'),
			  ('Medico','', 'medico@example.com'),
			  ('Electrisista','Juanitos','electrisista.juanitos@example.com'),
			  ('Pablo','Cesar','pablo.cesar@example.com');
			""")
			print('Seeded tutors table with default tutors')
		else:
			print(f'tutors table already has {count} rows')
	except Exception as e:
		print('ensure_tutors_seeded: skipped due to error:', e)

if __name__ == '__main__':
	# try to ensure tutors table is present and seeded (best-effort)
	ensure_tutors_seeded()
	app.run(debug=True)
from flask import Flask, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime
import re
from config.mysqlconnection import connectToMySQL

app = Flask(__name__)
app.secret_key = 'replace-this-secret'  # reemplaza antes de producción
DB = 'certificacion'
EMAIL_RE = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

# register blueprints (controllers)
from controllers.usuarios import usuarios_bp
from controllers.asesorias import asesorias_bp
app.register_blueprint(usuarios_bp)
app.register_blueprint(asesorias_bp)

if __name__ == '__main__':
	app.run(debug=True)


# Ruta de depuración: lista usuarios (solo si app.debug)
@app.route('/debug/usuarios')
def debug_usuarios():
	if not app.debug:
		return 'Not available', 404
	mysql = connectToMySQL(DB)
	users = mysql.query_db('SELECT id, nombre, apellido, email FROM users')
	# render simple HTML table for quick verification
	rows = ['<tr><th>id</th><th>nombre</th><th>apellido</th><th>email</th></tr>']
	for u in users:
		rows.append(f"<tr><td>{u.get('id')}</td><td>{u.get('nombre')}</td><td>{u.get('apellido')}</td><td>{u.get('email')}</td></tr>")
	html = '<h2>Usuarios en la BD</h2><table border="1">' + '\n'.join(rows) + '</table>'
	return html
from flask import Flask, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime
import re
from config.mysqlconnection import connectToMySQL

app = Flask(__name__)
app.secret_key = 'replace-this-secret'  # reemplaza antes de producción
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
	# unique email
	mysql = connectToMySQL(DB)
	existing = mysql.query_db('SELECT id FROM users WHERE email=%(email)s', {'email': email})
	if existing:
		errors.append('Email ya registrado')
	return errors

@app.route('/')
def index():
	if not session.get('user_id'):
		return redirect('/login')
	mysql = connectToMySQL(DB)
	today = date.today().isoformat()
	# Por defecto incluimos todas; para bonus filtramos fechas pasadas
	asesorias = mysql.query_db('SELECT a.*, u.nombre as solicitante, u.id as usuario_id FROM asesorias a JOIN users u on a.usuario_id = u.id WHERE a.fecha >= %(today)s ORDER BY a.fecha', {'today': today})
	return render_template('dashboard.html', asesorias=asesorias)

@app.route('/register', methods=['GET','POST'])
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

@app.route('/login', methods=['GET','POST'])
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
@app.route('/logout')
def logout():
	session.clear()
	return redirect('/login')

def proteger_sesion():
	if not session.get('user_id'):
		flash('Debe iniciar sesión', 'error')
		return redirect('/login')
@app.route('/asesoria/nueva', methods=['GET','POST'])
def nueva_asesoria():
	if not session.get('user_id'):
		flash('Debe iniciar sesión para solicitar asesoría', 'error')
		return redirect('/login')
	mysql = connectToMySQL(DB)
	usuarios = mysql.query_db('SELECT id, nombre, apellido FROM users')
	if request.method == 'GET':
		# exclude current user from tutor list
		usuarios = [u for u in usuarios if u['id'] != session['user_id']]
		return render_template('asesoria_nueva.html', usuarios=usuarios, asesoria=None)
	# POST - validar
	tema = request.form.get('tema','').strip()
	fecha_s = request.form.get('fecha','')
	duracion_s = request.form.get('duracion','')
	notas = request.form.get('notas','').strip()
	tutor_id = request.form.get('tutor_id')
	errors = []
	if not tema:
		errors.append('Tema no puede estar vacío')
	try:
		fecha_obj = datetime.strptime(fecha_s, '%Y-%m-%d').date()
	except Exception:
		errors.append('Fecha inválida')
		fecha_obj = None
	if fecha_obj and fecha_obj < date.today():
		errors.append('La fecha no puede estar en el pasado')
	try:
		duracion = int(duracion_s)
		if duracion < 1 or duracion > 8:
			errors.append('Duración debe estar entre 1 y 8')
	except Exception:
		errors.append('Duración inválida')
	if len(notas) > 50:
		errors.append('Notas no puede tener más de 50 caracteres')
	if errors:
		for e in errors:
			flash(e, 'error')
		usuarios = [u for u in usuarios if u['id'] != session['user_id']]
		return render_template('asesoria_nueva.html', usuarios=usuarios, asesoria=request.form)
	query = 'INSERT INTO asesorias (tema, fecha, duracion, notas, usuario_id, tutor_id) VALUES (%(tema)s, %(fecha)s, %(duracion)s, %(notas)s, %(usuario_id)s, %(tutor_id)s)'
	data = {
	'tema': tema,
	'fecha': fecha_s,
	'duracion': duracion,
	'notas': notas,
		'usuario_id': session['user_id'],
		'tutor_id': tutor_id if tutor_id else None
	}
	mysql.query_db(query, data)
	flash('Asesoría creada', 'success')
	return redirect('/')
@app.route('/asesoria/ver/<int:id>')
def ver_asesoria(id):
	mysql = connectToMySQL(DB)
	a = mysql.query_db('SELECT a.*, u.nombre as solicitante, u.apellido as solicitante_ap FROM asesorias a JOIN users u on a.usuario_id=u.id WHERE a.id=%(id)s', {'id': id})
	if not a:
		flash('Asesoría no encontrada', 'error')
		return redirect('/')
	asesoria = a[0]
	usuarios = mysql.query_db('SELECT id, nombre, apellido FROM users')
	tutor_actual = mysql.query_db('SELECT id, nombre, apellido FROM users WHERE id=%(id)s', {'id': asesoria.get('tutor_id')})
	tutor_actual = tutor_actual[0] if tutor_actual else {'id': None, 'nombre':'N/A','apellido':''}
	return render_template('asesoria_ver.html', asesoria=asesoria, usuarios=usuarios, tutor_actual=tutor_actual, solicitante=asesoria.get('solicitante'))

@app.route('/asesoria/cambiar_tutor/<int:id>', methods=['POST'])
def cambiar_tutor(id):
	if not session.get('user_id'):
		flash('Debe iniciar sesión', 'error')
		return redirect('/login')
	tutor_id = request.form.get('tutor_id')
	mysql = connectToMySQL(DB)
	mysql.query_db('UPDATE asesorias SET tutor_id=%(tutor_id)s WHERE id=%(id)s', {'tutor_id': tutor_id, 'id': id})
	flash('Tutor actualizado', 'success')
	return redirect(f'/asesoria/ver/{id}')

@app.route('/asesoria/editar/<int:id>', methods=['GET','POST'])
def editar_asesoria(id):
	if not session.get('user_id'):
		flash('Debe iniciar sesión', 'error')
		return redirect('/login')
	mysql = connectToMySQL(DB)
	a = mysql.query_db('SELECT * FROM asesorias WHERE id=%(id)s', {'id': id})
	if not a:
		flash('Asesoría no encontrada', 'error')
		return redirect('/')
	asesoria = a[0]
	if asesoria['usuario_id'] != session['user_id']:
		flash('No autorizado', 'error')
		return redirect('/')
	usuarios = mysql.query_db('SELECT id, nombre, apellido FROM users')
	usuarios = [u for u in usuarios if u['id'] != asesoria['usuario_id']]
	if request.method == 'GET':
		return render_template('asesoria_editar.html', asesoria=asesoria, usuarios=usuarios)
	# POST: validar
	tema = request.form.get('tema','').strip()
	fecha_s = request.form.get('fecha','')
	duracion_s = request.form.get('duracion','')
	notas = request.form.get('notas','').strip()
	tutor_id = request.form.get('tutor_id')
	errors = []
	if not tema:
		errors.append('Tema no puede estar vacío')
	try:
		fecha_obj = datetime.strptime(fecha_s, '%Y-%m-%d').date()
	except Exception:
		errors.append('Fecha inválida')
		fecha_obj = None
	if fecha_obj and fecha_obj < date.today():
		errors.append('La fecha no puede estar en el pasado')
	try:
		duracion = int(duracion_s)
		if duracion < 1 or duracion > 8:
			errors.append('Duración debe estar entre 1 y 8')
	except Exception:
		errors.append('Duración inválida')
	if len(notas) > 50:
		errors.append('Notas no puede tener más de 50 caracteres')
	if errors:
		for e in errors:
			flash(e, 'error')
		return render_template('asesoria_editar.html', asesoria=request.form, usuarios=usuarios)
	mysql.query_db('UPDATE asesorias SET tema=%(tema)s, fecha=%(fecha)s, duracion=%(duracion)s, notas=%(notas)s, tutor_id=%(tutor_id)s WHERE id=%(id)s', {'tema':tema,'fecha':fecha_s,'duracion':duracion,'notas':notas,'tutor_id':tutor_id,'id':id})
	flash('Asesoría actualizada', 'success')
	return redirect('/')
@app.route('/asesoria/borrar/<int:id>')
def borrar_asesoria(id):
	if not session.get('user_id'):
		flash('Debe iniciar sesión', 'error')
		return redirect('/login')
	mysql = connectToMySQL(DB)
	a = mysql.query_db('SELECT * FROM asesorias WHERE id=%(id)s', {'id': id})
	if not a:
		flash('Asesoría no encontrada', 'error')
		return redirect('/')
	asesoria = a[0]
	if asesoria['usuario_id'] != session['user_id']:
		flash('No autorizado', 'error')
		return redirect('/')
	mysql.query_db('DELETE FROM asesorias WHERE id=%(id)s', {'id': id})
	flash('Asesoría borrada', 'success')
	return redirect('/')

if __name__ == '__main__':
	app.run(debug=True)
