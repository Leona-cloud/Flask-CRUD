from flask import Flask, request, jsonify
import logging

from flask_mysqldb import MySQL
import MySQLdb.cursors
from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash, check_password_hash


load_dotenv()

logging.basicConfig(level =logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)

with app.app_context():
        try:
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT 1')
            cursor.close()
            logger.info("Database connection established successfully.")
        except Exception as e:
            logger.error(f"Error connecting to the database: {e}")



def log_request_info():
     logger.info(f"Request: {request.method} {request.url}")


@app.route('/register', methods=['POST'])
def add_user():
     data = request.get_json()
     name = data["name"]
     email = data["email"]
     username = data["username"]
     password = data["password"]

     hashed_password = generate_password_hash(password)

     cursor = mysql.connection.cursor()
     cursor.execute('INSERT INTO users (name, email, username, password) VALUES (%s, %s, %s, %s)', (name, email, username, hashed_password))
     mysql.connection.commit()
     logger.info(f"Added user: {name}, {email}")
     return jsonify({"success": "true", "message": "User added successfully" }), 201


@app.route('/users', methods=['GET'])
def fetch_users():
     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
     cursor.execute('SELECT * FROM users')
     users = cursor.fetchall()
     logger.info('Users fetched successfully')
     return jsonify({"success": "true", "message": "Users fetched successfully", "users": users}),201


@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE id = %s', (id,))
    user = cursor.fetchone()
    if user:
        logger.info(f"Retrieved user with id: {id}")
        return jsonify({"success": "true", "message": "User fetched successfully", "user": user}), 201
    else:
        logger.warning(f"User with id: {id} not found")
        return jsonify({'success': 'false','message': 'User not found!'}), 404



@app.route('/user/<int:id>', methods=['PUT'])
def update_user(id):
     data = request.get_json()
     name = data['name']
     email = data['email']
     password = data['password']

     cursor = mysql.connection.cursor()

     if password:
          hash_password = generate_password_hash(password)
          cursor.execute('UPDATE users SET name = %s, email = %s, password = %s WHERE id = %s', (name, email, hash_password, id))
     else:
          cursor.execute('UPDATE users SET name = %s, email = %s WHERE id = %s', (name, email, id))
     mysql.connection.commit()
     logger.info(f"User details updated successfully")
     return jsonify({"success": "true", "message": "User details updated successfully"}),201




@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_user(id):
     cursor = mysql.connection.cursor()
     cursor.execute('DELETE FROM users WHERE id = %s', (id,))
     mysql.connection.commit()
     logger.info(f"User with id:{id} has been deleted")
     return jsonify({"success":"true", "message": "User deleted successfully"})
     
 



if __name__ == '__main__':
    app.run(debug= True)