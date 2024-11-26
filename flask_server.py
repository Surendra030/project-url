from flask import Flask, request, jsonify
from final_script import main
from flask_lambda import FlaskLambda

app = Flask(__name__)

@app.route('/process-url', methods=['POST'])
def process_url():
    try:
        # Parse the incoming JSON data
        data = request.get_json()
        url = data.get('url')

        if not url:
            return jsonify({"error": "Missing 'url' in request data"}), 400

        # Pass the URL to your main function
        main(url)

        return jsonify({"message": "Processing started successfully", "url": url}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

