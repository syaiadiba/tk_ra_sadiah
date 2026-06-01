# test_minimal.py
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Server TK RA SA'DIAH BERJALAN!"

if __name__ == '__main__':
    print("🚀 Mencoba menjalankan server di port 5000...")
    app.run(debug=True, host='127.0.0.1', port=5000)