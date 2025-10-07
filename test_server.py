from app import create_app
import traceback

try:
    app = create_app()
    print("App created successfully")
    print("Starting server...")
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()