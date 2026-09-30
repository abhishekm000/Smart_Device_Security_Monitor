from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    print("Starting Smart Device Security Monitor Backend...")
    app.run(host='0.0.0.0', port=5000, debug=True)
