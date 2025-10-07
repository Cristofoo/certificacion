from config.mysqlconnection import connectToMySQL
from datetime import date

DB = 'certificacion'

class Asesoria:
    @staticmethod
    def create(tema, fecha, duracion, notas, usuario_id, tutor_id=None):
        mysql = connectToMySQL(DB)
        query = 'INSERT INTO asesorias (tema, fecha, duracion, notas, usuario_id, tutor_id) VALUES (%(tema)s, %(fecha)s, %(duracion)s, %(notas)s, %(usuario_id)s, %(tutor_id)s)'
        data = {'tema': tema, 'fecha': fecha, 'duracion': duracion, 'notas': notas, 'usuario_id': usuario_id, 'tutor_id': tutor_id}
        return mysql.query_db(query, data)

    @staticmethod
    def get_by_id(id):
        mysql = connectToMySQL(DB)
        res = mysql.query_db('SELECT * FROM asesorias WHERE id=%(id)s', {'id': id})
        return res[0] if res else None

    @staticmethod
    def update(id, tema, fecha, duracion, notas, tutor_id):
        mysql = connectToMySQL(DB)
        mysql.query_db('UPDATE asesorias SET tema=%(tema)s, fecha=%(fecha)s, duracion=%(duracion)s, notas=%(notas)s, tutor_id=%(tutor_id)s WHERE id=%(id)s', {'tema':tema,'fecha':fecha,'duracion':duracion,'notas':notas,'tutor_id':tutor_id,'id':id})

    @staticmethod
    def delete(id):
        mysql = connectToMySQL(DB)
        mysql.query_db('DELETE FROM asesorias WHERE id=%(id)s', {'id': id})

    @staticmethod
    def upcoming():
        mysql = connectToMySQL(DB)
        today = date.today().isoformat()
        return mysql.query_db('SELECT a.*, u.nombre as solicitante, u.id as usuario_id FROM asesorias a JOIN users u on a.usuario_id = u.id WHERE a.fecha >= %(today)s ORDER BY a.fecha', {'today': today})
