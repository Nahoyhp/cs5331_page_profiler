import requests
import json
import subprocess
from bs4 import BeautifulSoup
import difflib
import re

response = {'rows': [{'end': False, 'left': {'chunks': [{'value': 'roses are ', 'type': 'equal'}, {'value': 'red', 'type': 'remove'}], 'line': 1}, 'right': {'chunks': [{'value': 'roses are ', 'type': 'equal'}, {'value': 'green', 'type': 'insert'}], 'line': 1}, 'insideChanged': True, 'start': True}, {'end': True, 'left': {'chunks': [{'value': '', 'type': 'remove'}, {'value': 'violets are ', 'type': 'equal'}, {'value': 'blue', 'type': 'remove'}], 'line': 2}, 'right': {'chunks': [{'value': '', 'type': 'insert'}, {'value': 'violets are ', 'type': 'equal'}, {'value': 'purple', 'type': 'insert'}], 'line': 2}, 'insideChanged': True}], 'added': 3, 'removed': 3}

reference = """<html>
<head>
<title>Thank you!</title>
</head>
<body>
<p><img src ="/logo.png" alt="" width="243" height="102"></p>
<h1> Thank you! </h1>
<p id="msg"> Your registration to this event has been recorded as follows:</p>
<p>Name:</p>
<p>Email:</p>
<p>Food preference: Swedish meatballs</p>
</body>
</html>
"""

inject = """
<html>
<head>
<title>Thank you!</title>
</head>
<body>
<p><img src ="/logo.png" alt="" width="243" height="102"></p>
<h1> Thank you! </h1>
<p id="msg"> Your registration to this event has been recorded as follows:</p>
<p>Name:\n<script>\nalert('XSS')\n</script>\n</p>
<p>Email:</p>
<p>Food preference: Swedish meatballs</p>
</body>
</html>
"""

def format_start(html_string):
  return re.sub(r".*<[. ]+>", lambda x: x.group(0) + "\n", html_string)

def format_end(html_string):
  return re.sub(r".*[a-z ]*</[a-z]*>", lambda x: "\n" + x.group(0) + "\n", html_string)


def find_difference(left, right):
  email = "xiaophyolin@gmail.com"

  url = 'https://api.diffchecker.com/public/text?output_type=json&email=' + email 
  myobj = {
  "output_type" : "json",
  "left" : left,
  "right": right,
  "diff_level": "word"
  }

  return requests.post(url, json = myobj).json()

def difference_right(json_item):
  if json_item['added'] == 0 and json_item['removed'] == 0:
    return 0

  inserted = []
  # each line_dic represents the difference in one line
  
  consecutive_inject = ""
  for line_dic in json_item['rows']:
    if line_dic['insideChanged'] == False:
      continue

    for index, comparison_dic in enumerate(line_dic['right']['chunks']):
      #type can be "equal", "remove", "insert"
      if comparison_dic['type'] == "insert":
        consecutive_inject += comparison_dic['value']
        continue

      inserted.append(consecutive_inject)
      consecutive_inject = ""
      continue

  if consecutive_inject != "":
    inserted.append(consecutive_inject)

  return inserted

def run_php(command_line):
  #Try to run the line as php. Run True if possible.
  #Ideally in a docker.
  return False

def run_js(inject_line):
  #Try to run the line as php. Run True if possible.
  #Ideally in a docker.
  return True



def test_inserts_runnable(inserted_lines):
  flag = False
  for line in inserted_lines:
    # Will help to insert missing tags
    line_soup = BeautifulSoup(line, 'html.parser')
    for d in line_soup.descendants():
      print(d)
      # Try to run each descandants to see if they are runnable.
      # If so, return true.

def test():
  result_json = find_difference(reference, inject)
  result = difference_right(result_json)
  return (result_json, result)

if __name__ == "__main__":
  # Step 1: Format the reference and Inject HTML
    # format_start(), format_end()

  # Step 2: Find the difference between Reference and Inject
    # find_difference() -> Query diff checker api
    # find_right() -> Find the inserts in the Inject. If possible, try to connect the consective inserts.
    
  # Step 3: Try to run each of the difference to see if they are runnable
    # test_inserts_runnable()