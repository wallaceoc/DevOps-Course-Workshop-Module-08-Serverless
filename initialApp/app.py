from flask import Flask
import time


app = Flask(__name__)


@app.route("/")
def day():
    start = time.time()
    time.sleep(5) # Simulating 5 seconds of cpu-intensive processing
    end = time.time()
    processingTime = end - start
    return "Processing took " + str(processingTime)  + " seconds"
