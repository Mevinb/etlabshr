from app import create_app

if __name__ == "__main__":
    app = create_app()
    print("Starting Flask app...")
    try:
        app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
    except Exception as e:
        print(f"Error starting app: {e}")
        import traceback
        traceback.print_exc()