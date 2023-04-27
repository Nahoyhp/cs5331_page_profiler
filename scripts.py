import requests
from bs4 import BeautifulSoup

from pathlib import Path


#Machine Learning Component
from transformers import TextClassificationPipeline, RobertaTokenizer, RobertaConfig, RobertaModel, RobertaForSequenceClassification

from pathlib import Path

CODEBERTA_LANGUAGE_ID = "huggingface/CodeBERTa-language-id"

CODEBERTA_PIPELINE = TextClassificationPipeline(
    model=RobertaForSequenceClassification.from_pretrained(CODEBERTA_LANGUAGE_ID),
    tokenizer=RobertaTokenizer.from_pretrained(CODEBERTA_LANGUAGE_ID)
)

def test_inserts_runnable(inserted_lines):
  for line in inserted_lines:
    # Will help to insert missing tags
    line_soup = BeautifulSoup(line, 'html.parser')

    #If line = "<p> <b1> X </b1> <h2> <h3> Y </h3> </h2> </p>"
    #descandants will be "<b1> X </b1>", "<h2> <h3> Y </h3> </h2>", "<h3> Y </h3>""
    for d in line_soup.descendants:
      str_d = str(d)
      # Seems like ML model can't accept string length greater than that
      if len(str_d) > 514:
        continue

      if len(str_d) >= 10 and isCode(str(d)):
        return True
    
  return False

def isCode(testString):
  berta_result = CODEBERTA_PIPELINE(testString.strip())[0]
  label, score = berta_result['label'], berta_result['score']
  if label in ['javascript', 'php'] and score > 0.85:
    print(testString, label, score)
    return True
  return False


def open_files(filepath_1, filepath_2):
  try:
    with open(filepath_1, "r") as file1, open(filepath_2, "r") as file2:
      # Process the contents of the files here
      file1_contents = file1.read()
      file2_contents = file2.read()
      return file1_contents, file2_contents
  
  except:
    print("Something went wrong when opening reference.txt and/or requested.txt")


line_num_to_line_dict = {}

# removes the outermost common chars of string1
def remove_common_chars(string1, string2):
    ptr1_left = 0
    ptr2_left = 0

    while ptr1_left < len(string1) and ptr2_left < len(string2):
        if string1[ptr1_left] == string2[ptr2_left]:
            ptr1_left += 1
            ptr2_left += 1
        else:
            break

    string2 = string2[ptr2_left:len(string2)]

    ptr1_right = len(string1) - 1
    ptr2_right = len(string2) - 1

    while ptr1_right >= 0 and ptr2_right >= 0:
        if string1[ptr1_right] == string2[ptr2_right]:
            ptr1_right -= 1
            ptr2_right -= 1
        else:
            break

    return string2[0:ptr2_right + 1]

def compare_pages(ref_page, req_page):
    line_num_to_line_dict.clear()
    ref_lines = ref_page.split("\n")
    req_lines = req_page.split("\n")
    num_lines = min(len(ref_lines), len(req_lines))

    # lines that are not the same
    for i in range(num_lines):
        if ref_lines[i] != req_lines[i]:
            line_num_to_line_dict[i] = remove_common_chars(ref_lines[i], req_lines[i])

    # additional lines from requested.txt page are added
    if len(req_lines) > len(ref_lines):
        for i in range(num_lines, len(req_lines)):
            line_num_to_line_dict[i] = req_lines[i]

if __name__ == "__main__":
  #Query the diffChecker API to find the difference between left (base) and right (web page of interest)
  reference, requested = open_files("./reference.txt", "./request.txt")
  compare_pages(reference, requested)

  if test_inserts_runnable(line_num_to_line_dict.values()):
    print("2")
  else:
    print("1")

  print("Testing Injected")

  reference, requested = open_files("./reference.txt", "./request_injected.txt")
  compare_pages(reference, requested)

  if test_inserts_runnable(line_num_to_line_dict.values()):
    print("2")
  else:
    print("1")
     

