# Binbin Ji
# bj2414

from flask import Flask, request, jsonify
import socket
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/register', methods=['PUT'])
def register():
    try:
        data = request.json
        logging.info(f"Received registration request: {data}")
        hostname = data.get('hostname')
        ip = data.get('ip')
        as_ip = data.get('as_ip')
        as_port = data.get('as_port')

        if not all([hostname, ip, as_ip, as_port]):
            logging.error(f"Missing parameters in registration request: {data}")
            return "Bad Request: Missing parameters", 400

        # Register with AS
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            message = f"TYPE=A\nNAME={hostname}\nVALUE={ip}\nTTL=10"
            logging.info(f"Sending registration message to AS: {message}")
            s.sendto(message.encode(), (as_ip, int(as_port)))

        logging.info("Registration successful")
        return "Created", 201
    except Exception as e:
        logging.exception(f"Error during registration: {str(e)}")
        return "Internal Server Error", 500

@app.route('/fibonacci')
def fibonacci():
    try:
        number = request.args.get('number')
        logging.info(f"Received Fibonacci request for number: {number}")
        
        if not number or not number.isdigit():
            logging.error(f"Invalid number in Fibonacci request: {number}")
            return "Bad Request: Invalid number", 400

        n = int(number)
        result = calculate_fibonacci(n)
        logging.info(f"Calculated Fibonacci number {n}: {result}")
        return jsonify({"fibonacci": result}), 200
    except Exception as e:
        logging.exception(f"Error calculating Fibonacci number: {str(e)}")
        return "Internal Server Error", 500

def calculate_fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

if __name__ == '__main__':
    logging.info("Starting Fibonacci Server...")
    app.run(host='0.0.0.0', port=9090)