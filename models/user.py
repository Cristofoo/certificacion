from config.mysqlconnection import connectToMySQL

DB = 'certificacion'

class User:
    @staticmethod
    def create(nombre, apellido, email, password):
        mysql = connectToMySQL(DB)
        query = 'INSERT INTO users (nombre, apellido, email, password) VALUES (%(nombre)s, %(apellido)s, %(email)s, %(password)s)'
        data = {'nombre': nombre, 'apellido': apellido, 'email': email, 'password': password}
        return mysql.query_db(query, data)

    @staticmethod
    def get_by_email(email):
        mysql = connectToMySQL(DB)
        res = mysql.query_db('SELECT * FROM users WHERE email=%(email)s', {'email': email})
        return res[0] if res else None

    @staticmethod
    def get_by_id(user_id):
        mysql = connectToMySQL(DB)
        res = mysql.query_db('SELECT * FROM users WHERE id=%(id)s', {'id': user_id})
        return res[0] if res else None

    @staticmethod
    def all_users():
        mysql = connectToMySQL(DB)
        return mysql.query_db('SELECT id, nombre, apellido FROM users')
