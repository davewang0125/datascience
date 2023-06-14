import requests 
from flask import Flask, jsonify 
# ... 
@app.route('/stock/') 
def integrate_with_third_party():
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-summary" 
    querystring = {"symbol": "ARMN ,"region":"US"} 
    headers = { 
        'x-rapidapi-key': "apikey", 
        'x-rapidapi-host': 'apidojo-yahoo-finance-v1.p.rapidapi.com' 
    } 
    response = requests.request("GET", url, headers=headers, params=querystring) 
    print(response.text)
# ... 
@app.route('/stock/<string:symbol>') 
def integrate_with_third_party(symbol): 
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-summary" 
    querystring = {"symbol": symbol ,"region":"US"} 
    headers = { 
        'x-rapidapi-key': "API key", 
        'x-rapidapi-host': 'apidojo-yahoo-finance-v1.p.rapidapi.com' 
    } 
    response = requests.request("GET", url, headers=headers, params=querystring) 
    to_json = response.json() 
    try: 
        price = to_json.get('price') 
        reg_price = price.get('regularMarketPrice') 
    except (KeyError, AttributeError): 
        return 'No price could be found for that symbol.' 
    return jsonify(reg_price)