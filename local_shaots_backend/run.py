""" Entry point to start Flask """
from app import boot_app

app = boot_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)