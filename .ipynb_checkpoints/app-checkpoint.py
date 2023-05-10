import numpy as np
import random
from flask import Flask, request, jsonify, render_template
import pickle
import joblib

# Create flask app
flask_app=Flask(__name__, template_folder='templates', static_folder='static')
#flask_app = Flask(__name__)
model = joblib.load(open("model_GBP.pkl", "rb"))

@flask_app.route("/")
def Home():
    return render_template("index.html")
    return render_template("styles.css")

@flask_app.route("/pred", methods = ["POST"])
def predict():
    float_features = [float(x) for x in request.form.values()]
    features = [np.array(float_features)]
    prediction = model.predict(features)
    # return render_template("index.html", prediction_text = "The flower species is {}".format(prediction))
    return render_template("index.html", prediction_text = f'The flower species is {prediction}')
# if __name__ == "__main__":
#     flask_app.run(debug=True)

if __name__ == "__main__":  # Makes sure this is the main process
	flask_app.run( # Starts the site
		host='0.0.0.0',  # EStablishes the host, required for repl to detect the site
		port=random.randint(2000, 9000)  # Randomly select the port the machine hosts on.
	)