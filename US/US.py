# Binbin Ji
# bj2414

from flask import Flask, request
import socket
import requests
import logging
import traceback

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/fibonacci')
def fibonacci():
    try:
        # Get parameters from the request
        hostname = request.args.get('hostname')
        fs_port = request.args.get('fs_port')
        number = request.args.get('number')
        as_ip = request.args.get('as_ip')
        as_port = request.args.get('as_port')

        logging.info(f"Received request with params: hostname={hostname}, fs_port={fs_port}, number={number}, as_ip={as_ip}, as_port={as_port}")

        # Check if all parameters are present
        if not all([hostname, fs_port, number, as_ip, as_port]):
            missing = [p for p in ['hostname', 'fs_port', 'number', 'as_ip', 'as_port'] if not request.args.get(p)]
            logging.error(f"Missing parameters: {', '.join(missing)}")
            return f"Bad Request: Missing parameters: {', '.join(missing)}", 400

        # Query AS to get the IP address of the hostname
        logging.info(f"Querying AS at {as_ip}:{as_port} for hostname: {hostname}")
        fs_ip = query_as(hostname, as_ip, as_port)
        if not fs_ip:
            logging.error(f"Couldn't resolve hostname: {hostname}")
            return f"Not Found: Couldn't resolve hostname {hostname}", 404

        logging.info(f"Resolved {hostname} to {fs_ip}")

        # Query FS to get the Fibonacci number
        try:
            fs_url = f"http://{fs_ip}:{fs_port}/fibonacci?number={number}"
            logging.info(f"Querying FS at: {fs_url}")
            response = requests.get(fs_url, timeout=5)
            if response.status_code == 200:
                logging.info(f"Received response from FS: {response.text}")
                return response.text, 200
            else:
                logging.error(f"Error response from FS: {response.status_code} - {response.text}")
                return f"Error: Couldn't get Fibonacci number. Status: {response.status_code}", 500
        except requests.RequestException as e:
            logging.error(f"Error connecting to Fibonacci Server: {str(e)}")
            return f"Error: Couldn't connect to Fibonacci Server. {str(e)}", 500

    except Exception as e:
        logging.exception(f"Unexpected error in fibonacci route: {str(e)}")
        return f"Internal Server Error: {str(e)}", 500

def query_as(hostname, as_ip, as_port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            message = f"TYPE=A\nNAME={hostname}"
            logging.info(f"Sending DNS query to AS: {message}")
            s.sendto(message.encode(), (as_ip, int(as_port)))
            s.settimeout(5)  # Set a 5-second timeout
            data, _ = s.recvfrom(1024)
            response = data.decode().split('\n')
            logging.info(f"Received response from AS: {response}")
            for line in response:
                if line.startswith("VALUE="):
                    return line.split("=")[1]
        logging.error("No VALUE found in AS response")
        return None
    except socket.timeout:
        logging.error(f"Timeout while querying AS at {as_ip}:{as_port}")
        return None
    except Exception as e:
        logging.exception(f"Error in query_as: {str(e)}")
        return None

if __name__ == '__main__':
    logging.info("Starting User Server...")
    app.run(host='0.0.0.0', port=8080, debug=True)