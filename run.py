import logging
import traceback

# Configure logging at the very start
logging.basicConfig(
    filename='error.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(message)s'
)

from app import create_app
from app.admin_routes import register_admin_routes

app = create_app()   # First create the app instance

register_admin_routes(app)  # Then register admin routes on the app

@app.errorhandler(Exception)
def handle_exception(e):
    tb = traceback.format_exc()
    logging.error("Unhandled Exception:\n" + tb)
    print("Unhandled Exception:\n" + tb)  # Also print on console
    return "Internal server error occurred. Please try again later.", 500

@app.route('/cause_error')
def cause_error():
    raise Exception("This is a test error to check logging.")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
