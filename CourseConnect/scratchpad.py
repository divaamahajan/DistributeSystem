
import json
import os
import pandas as pd

folder1 = 'CourseConnect'
path = os.getcwd()
filepath = os.path.join(path, folder1 , "userInput.json")
df = pd.read_json(filepath)    
print(df)