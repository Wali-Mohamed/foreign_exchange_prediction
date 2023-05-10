#import numpy as np
from glob import glob

import pandas as pd
import random
from flask import Flask, request, jsonify, render_template, session
from datetime import timedelta
import pickle
import joblib
import requests
from config import settings
from data import SQLRepository, AlphaVantageAPI
from model import GarchModel
from arch.univariate.base import ARCHModelResult
import sqlite3
# %load_ext autoreload
# %autoreload 2

connection = sqlite3.connect(settings.db_name, check_same_thread=False)
repo =SQLRepository(connection=connection)


# Create flask app
flask_app=Flask(__name__, template_folder='templates', static_folder='static')
flask_app.secret_key="hello"
flask_app.permanent_session_lifetime=timedelta(hours=1)
#flask_app = Flask(__name__)


@flask_app.route("/")
def home():
    return render_template("base.html")
    #return render_template("styles.css")
@flask_app.route("/data")
def data_page():
    return render_template("index.html")

@flask_app.route("/get_data", methods=['GET','POST'])
def get_data():
    
    from_curr=request.form['from_c'].upper()
    to_curr=request.form['to_c'].upper()
    session.permanent=True
    session['from_curr']=from_curr
    session['to_curr']=to_curr
    
    
    currency_class= AlphaVantageAPI()
    df=currency_class.fx_daily(from_symbol=from_curr, to_symbol=to_curr, output_size='full')
    data1=df.head()
    data2=data1.close.values
    data=df.head().to_html()
    table_name=from_curr+'/'+to_curr
    return render_template("index.html", data=data, table_name=table_name)
    
@flask_app.route("/t", methods = ["GET", "POST"])
def train():
    curr1=session['from_curr']
    curr2=session['to_curr']
      
    class_model=GarchModel(from_curr=curr1,to_curr=curr2, repo=repo, use_new_data=True)
    class_model.wrangle_data(n_observations=2500)
    p=int(request.form['p'])
    q=int(request.form['q'])
    
    
    

    class_model.fit(p,q)
    pvalues1=class_model.pvalues.to_frame()
    pvalues1.pvalues=round(pvalues1.pvalues,4)
    data=pvalues1.to_html()
    class_model.dump()
   

    return render_template('index.html', model_pvalues=data )

@flask_app.route("/p", methods = ["POST"])
def predict():
    params = [x for x in request.form.values()]
    print(params)
    class_model=GarchModel(from_curr=params[0].upper(),to_curr=params[1].upper(), repo=repo, use_new_data=True)
    class_model.load()
    model=class_model.model
    
    prediction = model.forecast(horizon=int(params[2]),reindex=False).variance
    start_date=prediction.index[0] + pd.DateOffset(days=1)
    prediction_dates = pd.bdate_range(start=start_date, periods=int(params[2]), freq='B')
    prediction_index=[d for d in prediction_dates.strftime('%d/%m/%Y')]

    
    data1=prediction.values.flatten()**0.5
    data=[round(i,4) for i in data1]
    # df=pd.DataFrame(data, index=prediction_index)
    # df.reset_index(inplace=True)
    # df.columns=['Date','Volatility']
    # df_html=df.to_html()
    

    
    return render_template("index.html",  new_data=zip(prediction_index, data), date_header='Date', predictions_header='Volatility')
    #return render_template("index.html", date=prediction_index, prediction=data, date_header='Date', predictions_header='Volatility' )
# if __name__ == "__main__":
#     flask_app.run(debug=True)

if __name__ == "__main__":  # Makes sure this is the main process
	flask_app.run( # Starts the site
		host='0.0.0.0',  # EStablishes the host, required for repl to detect the site
		port=random.randint(2000, 9000),  # Randomly select the port the machine hosts on.
        debug=True
	)