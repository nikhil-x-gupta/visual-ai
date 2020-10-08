#
# util.py
#
# Sanjeev Gupta, April 2020

import requests

def inference_publish(url, inference_data_json):
    req = {}
    try:
        header = {"Content-type": "application/json", "Accept": "text/plain"} 
        req = requests.post(url, data=inference_data_json, headers=header)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt) 

    return ""
