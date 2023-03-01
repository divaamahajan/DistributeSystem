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

import json
	
# Data to be written
dictionary ={
"id": "04",
"name": "sunil",
"department": "HR"
}
	
# Serializing json
json_object = json.dumps(dictionary, indent = 4)
print(json_object)
print(type(json_obj))

y = (json.loads(json_object))["id"]

# the result is a Python dictionary:
print(y)
