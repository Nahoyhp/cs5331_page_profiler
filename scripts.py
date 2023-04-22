import requests
from bs4 import BeautifulSoup


#Machine Learning Component
from transformers import TextClassificationPipeline, RobertaTokenizer, RobertaConfig, RobertaModel, RobertaForSequenceClassification

from pathlib import Path


# import guesslang
# guess = guesslang.Guess()

"""
def test_guesslang(string):
  # guesslang.probabilities() return an list of tuples. (Langauge, Probabilities)
  # Find another model
  return list(filter(lambda x: x[0] in ['Php', 'JavaScript', 'HTML'], guess.probabilities(string)))
"""


"""
def format_start(html_string):
  return re.sub(r".*<[. ]+>", lambda x: x.group(0) + "\n", html_string)

def format_end(html_string):
  return re.sub(r".*[a-z ]*</[a-z]*>", lambda x: "\n" + x.group(0) + "\n", html_string)
"""

CODEBERTA_LANGUAGE_ID = "huggingface/CodeBERTa-language-id"

CODEBERTA_PIPELINE = TextClassificationPipeline(
    model=RobertaForSequenceClassification.from_pretrained(CODEBERTA_LANGUAGE_ID),
    tokenizer=RobertaTokenizer.from_pretrained(CODEBERTA_LANGUAGE_ID)
)

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
      
      if consecutive_inject != "":
        inserted.append(consecutive_inject)
        consecutive_inject = ""
        
  if consecutive_inject != "":
    inserted.append(consecutive_inject)

  return inserted

def test_inserts_runnable(inserted_lines):
  for line in inserted_lines:
    # Will help to insert missing tags
    line_soup = BeautifulSoup(line, 'html.parser')

    #If line = "<p> <b1> X </b1> <h2> <h3> Y </h3> </h2> </p>"
    #descandants will be "<b1> X </b1>", "<h2> <h3> Y </h3> </h2>", "<h3> Y </h3>""
    for d in line_soup.descendants:
      if isCode(str(d)):
        return True
    
  return False

def isCode(testString):
  berta_result = CODEBERTA_PIPELINE(testString)[0]
  label, score = berta_result['label'], berta_result['score']
  if label in ['javascript', 'php'] and score > 0.85:
    print(testString, label, score)
    return True
  
  return False

def test():
  result_json = find_difference(reference, inject)
  result = difference_right(result_json)
  return test_inserts_runnable(result)

if __name__ == "__main__":
  #Query the diffChecker API to find the difference between left (base) and right (web page of interest)
  referencePath = "./Base.txt"
  testPath = "./Test.txt"

  reference = Path(referencePath).read_text()
  inject = Path(testPath).read_text()

  difference_json = find_difference(reference, inject)

  #Find the inserts on the right page
  differences = difference_right(difference_json)

  #Test each one of the lines to see if they are runnable
  if test_inserts_runnable(differences):
    print("Contain Scripts")
  else:
    print("Good to Go")