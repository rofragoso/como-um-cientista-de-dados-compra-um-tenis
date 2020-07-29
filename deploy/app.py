import os.path
from flask import Flask, render_template ,request
import os
import json
import run_backend_r
import get_data_r
import ml_utils_r

import time

app = Flask(__name__)

def get_predictions():

    tenis = []
    
    novos_tenis_json = "novos_tenis.json"
    if not os.path.exists(novos_tenis_json):
        run_backend_r.update_db(1)
    
    last_update = os.path.getmtime(novos_tenis_json) * 1e9

    #if time.time_ns() - last_update > (720*3600*1e9): # aprox. 1 mes
    #    run_backend.update_db()

    with open("novos_tenis.json", 'r') as data_file:
        for line in data_file:
            line_json = json.loads(line)
            tenis.append(line_json)

    predictions = []
    
    for teniss in tenis:
        predictions.append(
                            {"link":teniss['link'],
                             "tenis":teniss['shoes'],
                             "score": float(teniss['score']),
                             "image":teniss['image']
                           }
                            )

    predictions = sorted(predictions, key = lambda x: x['score'], reverse = True)[:30]
           
    return predictions, last_update

@app.route('/')
def main_page():
    
    
    predictions,last_update = get_predictions()
    
    return render_template("index.html", predictions = predictions)


@app.route('/predict',endpoint='predict_api')
def predict_api():
    
    shoes_name = request.args.get("shoes_name", default='')
    shoes_page = get_data_r.download_shoes_page_api("/{}".format(shoes_name))
    
    shoes_json_data = get_data_r.parse_shoes_page(shoes_page)
    pre_feature_array=ml_utils_r.transform_all(shoes_json_data,shoes_name)
    
    if 'erro link imagem' in pre_feature_array['image']:
        output= {"shoes": "", "score": ""}
        return json.dumps(output)
    
    p=ml_utils_r.compute_prediction(pre_feature_array)
    output = {"shoes": shoes_name, "score": float(p)}
    
    return json.dumps(output)

@app.route('/update',endpoint='update_db_api')
def update_db_api():
    
    up = request.args.get("code", default='')
    pages= request.args.get("pages", default='')
    
    upp = "{}".format(up)
    if upp== 'censurado':
        run_backend_r.update_db(int(pages))
        return json.dumps("Database updated")
    else:
        output = {"Incorrect Code": 'err0' , "Pages": int(pages)}
        return json.dumps(output)
    

    
if __name__ ==  '__main__':
    app.run(debug = True, host = 'localhost')