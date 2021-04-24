from requests import *
import json
from datetime import datetime

payload = {
    "courier_type": 'воалвоало',

}
head = {'Content-Type': 'application/json', 'Accept': 'application/json'}
print(patch('http://127.0.0.1:5000/couriers/1', headers=head,
            json=payload, verify=False).json())
