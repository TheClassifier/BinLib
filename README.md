# BinLib
Python Class for querying doxbin

Usage:
```python
from BinLib import DoxBin
from random import choice

doxbin = DoxBin() # initialize doxbin class

session = doxbin.init_session() # initialize session to request dox content
if session is None: 
    print("Session initialized from session.json")
else:
    print("Session initialized from scratch")

query = input("Enter query: ")
while not query:
    query = input("Enter query: ")

dox_list = doxbin.search(query) # search for dox
print(dox_list)


dox_obj = choice(dox_list) # pick random dox from dox list
print(dox_obj)

dox_content = doxbin.get_dox_content(dox_obj['href']) # get dox content from dox url
print(dox_content)

```
