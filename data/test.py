from requests import *
import json
from datetime import datetime

payload = {
    "courier_type": "foot",

}
head = {'Content-Type': 'application/json', 'Accept': 'application/json'}
print(patch('http://localhost:5000/couriers/1', headers=head,
            json=payload, verify=False).json())
