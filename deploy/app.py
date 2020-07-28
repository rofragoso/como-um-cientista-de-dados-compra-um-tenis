import os.path
from flask import Flask, render_template
import os
import json
import run_backend_r

import time

app = Flask(__name__)

def get_predictions():

    tenis = []
    
    novos_tenis_json = "novos_tenis.json"
    if not os.path.exists(novos_tenis_json):
        run_backend_r.update_db()
    
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


if __name__ ==  '__main__':
    app.run(debug = True, host = 'localhost')