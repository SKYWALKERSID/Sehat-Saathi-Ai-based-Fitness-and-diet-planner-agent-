from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create all database tables on startup
        print("Database tables initialized successfully.")
    app.run(debug=True, host="127.0.0.1", port=5000, use_reloader=False)
