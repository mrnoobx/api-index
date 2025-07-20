from flask import Flask, request, jsonify
from terabox import get_direct_link

app = Flask(__name__)

@app.route('/api')
def api():
    url = request.args.get("q")
    if not url:
        return jsonify({"error": "Please provide q=url"}), 400

    try:
        result = get_direct_link(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
