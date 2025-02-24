from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["lancar_barokah"]
collection = db["sensor"]

@app.route("/upload", methods=["POST"])
def upload():
    try:
        data = request.json 
        collection.insert_one(data)
        
        return jsonify({"message": "Data stored successfully"}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
