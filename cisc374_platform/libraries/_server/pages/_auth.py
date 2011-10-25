from flask import request, jsonify
from cisc374 import app

@app.route('/login', methods=['GET', 'POST'])
def verify_permissions(type = 'student'):
    pass