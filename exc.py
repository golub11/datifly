import numpy as np
import pandas as pd

dic = [{'name': 'Nikola'}, {'name':'Milorad'}, {'name':'Masa'}]
print (dic[1]['name'])

# initialize list of lists
data = [['tom', 10], ['nick', 15], ['juli', 14]]

# Create the pandas DataFrame
df = pd.DataFrame(data, columns=['Name', 'Age'])

# print dataframe.
print(df.columns)

a = [[i] for i in df.columns]

print(a)