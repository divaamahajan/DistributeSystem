
# import necessary libraries
import pandas as pd
import os
  
folder1 = 'CourseConnect'
folder2 = 'courses'
def get_courses():
    path = os.getcwd()
    csv_file = os.path.join(path, folder1 , folder2, "CourseDetails.xlsx")
    df = pd.read_excel(csv_file) 
    desc_units = list(zip(df.description, df.units))
    courses = dict(zip(df.course, desc_units))
    return courses

def get_term():
    return ('winter', 'spring', 'summer','fall')

def get_year():
    return (2021, 2022, 2023)