from flask import Blueprint, render_template, request, redirect, session, flash
from config.mysqlconnection import connectToMySQL
from datetime import date, datetime

asesorias_bp = Blueprint('asesorias', __name__)
DB = 'certificacion'


@asesorias_bp.route('/')
def index():
    if not session.get('user_id'):
        return redirect('/login')
    mysql = connectToMySQL(DB)
    today = date.today().isoformat()
    asesorias = mysql.query_db('SELECT a.*, u.nombre as solicitante, u.id as usuario_id FROM asesorias a JOIN users u on a.usuario_id = u.id WHERE a.fecha >= %(today)s ORDER BY a.fecha', {'today': today})
    return render_template('dashboard.html', asesorias=asesorias)


@asesorias_bp.route('/asesoria/nueva', methods=['GET','POST'])
def nueva_asesoria():
    if not session.get('user_id'):
        flash('Debe iniciar sesión para solicitar asesoría', 'error')
        return redirect('/login')
    mysql = connectToMySQL(DB)
    usuarios = mysql.query_db('SELECT id, nombre, apellido FROM users')
    if request.method == 'GET':
        # exclude current user from potential tutors list
        usuarios = [u for u in usuarios if u['id'] != session['user_id']]
        return render_template('asesoria_nueva.html', usuarios=usuarios, asesoria=None, today=date.today().isoformat())
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
        return render_template('asesoria_nueva.html', usuarios=usuarios, asesoria=request.form.to_dict(), today=date.today().isoformat())

    # No hay errores: insertar
    query = 'INSERT INTO asesorias (tema, fecha, duracion, notas, usuario_id, tutor_id) VALUES (%(tema)s, %(fecha)s, %(duracion)s, %(notas)s, %(usuario_id)s, %(tutor_id)s)'
    data = {
        'tema': tema,
        'fecha': fecha_s,
        'duracion': duracion,
        'notas': notas,
        'usuario_id': session.get('user_id'),
        'tutor_id': int(tutor_id) if tutor_id else None
    }
    # Verificar que el usuario en sesión existe en la tabla users (evita errores FK)
    usuario_id = data.get('usuario_id')
    if not usuario_id:
        flash('No se reconoce al usuario en sesión. Inicia sesión de nuevo.', 'error')
        return redirect('/login')
    user_exists = mysql.query_db('SELECT id FROM users WHERE id=%(id)s', {'id': usuario_id})
    if not user_exists:
        flash('El usuario en sesión no existe en la base de datos. Inicia sesión de nuevo.', 'error')
        return redirect('/login')
    try:
        mysql.query_db(query, data)
    except Exception as e:
        # Manejo genérico: evitar mostrar stack trace en UI
        flash('Error al crear la asesoría: ' + str(e), 'error')
        return redirect('/')
    flash('Asesoría creada', 'success')
    return redirect('/')


@asesorias_bp.route('/asesoria/ver/<int:id>')
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


@asesorias_bp.route('/asesoria/cambiar_tutor/<int:id>', methods=['POST'])
def cambiar_tutor(id):
    if not session.get('user_id'):
        flash('Debe iniciar sesión', 'error')
        return redirect('/login')
    tutor_id = request.form.get('tutor_id')
    mysql = connectToMySQL(DB)
    # Solo el solicitante (usuario_id) puede cambiar el tutor
    a = mysql.query_db('SELECT * FROM asesorias WHERE id=%(id)s', {'id': id})
    if not a:
        flash('Asesoría no encontrada', 'error')
        return redirect('/')
    asesoria = a[0]
    if asesoria['usuario_id'] != session['user_id']:
        flash('Solo el solicitante puede cambiar el tutor', 'error')
        return redirect(f'/asesoria/ver/{id}')
    mysql.query_db('UPDATE asesorias SET tutor_id=%(tutor_id)s WHERE id=%(id)s', {'tutor_id': tutor_id, 'id': id})
    flash('Tutor actualizado', 'success')
    return redirect(f'/asesoria/ver/{id}')


@asesorias_bp.route('/asesoria/editar/<int:id>', methods=['GET','POST'])
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
        return render_template('asesoria_editar.html', asesoria=asesoria, usuarios=usuarios, today=date.today().isoformat())
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
        return render_template('asesoria_editar.html', asesoria=request.form.to_dict(), usuarios=usuarios, today=date.today().isoformat())

    # No hay errores: actualizar
    try:
        mysql.query_db('UPDATE asesorias SET tema=%(tema)s, fecha=%(fecha)s, duracion=%(duracion)s, notas=%(notas)s, tutor_id=%(tutor_id)s WHERE id=%(id)s', {'tema':tema,'fecha':fecha_s,'duracion':duracion,'notas':notas,'tutor_id':tutor_id,'id':id})
    except Exception as e:
        flash('Error al actualizar la asesoría: ' + str(e), 'error')
        return render_template('asesoria_editar.html', asesoria=request.form.to_dict(), usuarios=usuarios, today=date.today().isoformat())
    flash('Asesoría actualizada', 'success')
    return redirect('/')


@asesorias_bp.route('/asesoria/borrar/<int:id>')
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
