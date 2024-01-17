from flask import Flask
import time

app = Flask(__name__)

@app.route("/")
def process():
    start = time.time()
    time.sleep(5) # Simulating 5 seconds of cpu-intensive processing
    end = time.time()
    processingTime = end - start
    return f"Processing took {processingTime} seconds"
