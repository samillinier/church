import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

try:
    from vercel_app import app
    logging.info("Successfully imported application")
except Exception as e:
    logging.error(f"Failed to import application: {str(e)}")
    raise

if __name__ == "__main__":
    logging.info("Starting application")
    app.run() 