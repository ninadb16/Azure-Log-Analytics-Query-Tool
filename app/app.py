# app/app.py

from app import create_app
from dotenv import load_dotenv

app = create_app()

if __name__ == '__main__':
    load_dotenv()
    # You may need to change host/port depending on your environment
    app.run(host='127.0.0.1', port=5000, debug=True)
