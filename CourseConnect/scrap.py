import json
import threading
from queue import Queue

# JSON object
json_obj = """[
    {
        "name": "John",
        "age": 30,
        "city": "New York",
        "country": "USA"
    },
    {
        "name": "Emily",
        "age": 25,
        "city": "London",
        "country": "UK"
    },
    {
        "name": "Hiroshi",
        "age": 40,
        "city": "Tokyo",
        "country": "Japan"
    }
]"""
# import json

# # JSON string:
# # Multi-line string
x = """{
	"Name": "Jennifer Smith",
	"Contact Number": 7867567898,
	"Email": "jen123@gmail.com",
	"Hobbies":["Reading", "Sketching", "Horse Riding"]
	}"""

import pandas as pd

df = pd.read_json(x)  
print(df)
# # parse x:
# y = json.loads(json_obj)

# # the result is a Python dictionary:
# for row in y:
#     print(type(row))
    
# input = {"A":"a", "B":"b", "C":"c", "D":""}
# output = {k:v for (k,v) in input.items() if k in["A","B"] and v is not None}
# print(output)

