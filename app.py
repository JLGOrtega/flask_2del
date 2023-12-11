from flask import Flask, request, jsonify, render_template
import pickle
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime


app = Flask(__name__)

engine = create_engine("sqlite:///mydb.db")
with open("pipe_model.pkl", "rb") as f:
    loaded_model = pickle.load(f)
    


@app.route("/")
def hello():
    
    s = """
    <h1>APP FOR WINE PREDICTION</h1>
    <br>
    You need to call the endpoint "/predict" and pass the next values as args:
    <ul>
        <li>prol (proline): range 278-985</li>
        <li>flav (flavanoids): range 0.3-6</li>
        <li>col (color_intensity): range 1.28-13</li>
        <li>dilwin (od280/od315_of_diluted_wines): range 1.27-4</li>
        <li>alc (alcohol): range 11.0-15.0-985</li>
        <li>hue (hue): range 0.48-1.71</li>
        <li>phen (total_phenols): range 0.98-3.88</li>
    """
    return s


@app.route("/predict", methods=["GET"])
def predict():
    # GET ALL ARGS
    prol = request.args.get("prol")
    flav = request.args.get("flav")
    col = request.args.get("col")
    dilwin = request.args.get("dilwin")
    alc = request.args.get("alc")
    hue = request.args.get("hue")
    phen = request.args.get("phen")
    
    data2pred = [prol, flav, col, dilwin, alc, hue, phen]
    
    # IF ARGS MISSING, ERROR 0
    if None in data2pred:
        return {"results": 0}
    
    # IF ARGS NOT FLOAT, ERROR 1
    try:
        data2pred = [float(s) for s in data2pred]
    except:
        return {"results": 1}
    
    prediction = loaded_model.predict([data2pred])[0]
    
    # DATA TO UPLOAD
    fecha = str(datetime.now())[0:19]
    inputs = str(data2pred)
    output = prediction
    
    df = pd.DataFrame({
    "fecha": [fecha],
    "inputs": [inputs],
    "prediction": [output]
    })
    
    # UPLOAD
    df.to_sql("predictions", if_exists="append", con=engine, index=None)
    
    # RETURN PREDICTION
    return jsonify({"results": {"predcition":str(prediction)}})


@app.route("/predict_form", methods=["GET", "POST"])
def predict_form():
    if request.method == "POST":
        # GET ALL ARGS
        prol = request.form.get("prol")
        flav = request.form.get("flav")
        col = request.form.get("col")
        dilwin = request.form.get("dilwin")
        alc = request.form.get("alc")
        hue = request.form.get("hue")
        phen = request.form.get("phen")
        
        data2pred = [prol, flav, col, dilwin, alc, hue, phen]
        
        # IF ARGS MISSING, ERROR 0
        if None in data2pred:
            return {"results": 0}
        
        # IF ARGS NOT FLOAT, ERROR 1
        try:
            data2pred = [float(s) for s in data2pred]
        except:
            return {"results": 1}
        
        prediction = loaded_model.predict([data2pred])[0]
        
        # DATA TO UPLOAD
        fecha = str(datetime.now())[0:19]
        inputs = str(data2pred)
        output = prediction
        
        df = pd.DataFrame({
        "fecha": [fecha],
        "inputs": [inputs],
        "prediction": [output]
        })
        
        # UPLOAD
        df.to_sql("predictions", if_exists="append", con=engine, index=None)
        
        # RETURN PREDICTION
        return render_template('form.html', prediction = str(prediction))
    
    return render_template('form.html', prediction="N/A")

@app.route("/check_pred")
def check_pred():
    return pd.read_sql("SELECT * FROM predictions", con=engine).to_html()


app.run(debug=True)