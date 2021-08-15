from flask import Flask, request, jsonify
from flask.templating import render_template
from helpers import url_constructor, extract_and_parse, sort_func, format_date
from flask_cors import CORS
import requests, zipfile, io


app = Flask(__name__)
CORS(app)

LMP_BASE_URL = "http://oasis.caiso.com/oasisapi/SingleZip?queryname=PRC_LMP&version=1"

@app.route("/")
def show_homepage(): 
    """ Displays test homepage. """
    
    return render_template("./index.html")


@app.route("/api/LMP", methods=["POST"])
def get_zip_file(): 
    """ Retrieves zip file from CAISO API based on given parameters and
        returns parsed data in JSON. 
            accepts: 
                date format: yyyy-mm-dd
                market_id: DAM or RUC
                sample node: 0096WD_7_N001

            returns:
                {
                    header: {
                        "MKT_TYPE": "LMP",
                        "UOM": "US$/MWh"
                    },
                    data: {
                        "Congestion": [{interval, value}, ...],
                        "Energy": [{interval, value}, ...],
                        ...
                    }
                }
    """

    # construct url for request
    start_date = format_date(request.json["start_date"])
    end_date = format_date(request.json["end_date"])
    market_id = request.json["market_id"]
    node = request.json["node"]

    caiso_url = url_constructor(start_date, end_date, market_id, node)

    # make request to CAISO
    resp = requests.get(caiso_url)

    # stream file contents and get file name
    file = zipfile.ZipFile(io.BytesIO(resp.content))
    fileName = file.namelist()[0]

    # extract and parse file
    report = extract_and_parse(file, fileName)    
    
    # sorts data by interval number
    report['data'] = sort_func(report['data'])

    return jsonify(report)