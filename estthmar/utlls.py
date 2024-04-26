import re

# Function to parse and store questions and hints in a dictionary
def parse_questions(response_text):
    # Normalize text: replace different brackets with a unified format for easy parsing
    response_text = re.sub(r'\s+', ' ', response_text).replace('[', '(').replace(']', ')').replace('{', '(').replace('}', ')')

    # Dictionary to store the questions and hints
    questions_dict = {}

    # Regex to catch various question formats, including multiple hint formats
    pattern = r'(?i)\bQ(\d+)[.:!]\s*([^?!.]+[?!.])\s*(?:\(([^)]+)\)|- Example: ([^,]+),|Example: ([^,]+),)?'
    matches = re.findall(pattern, response_text)

    # Populate the dictionary with parsed data
    for match in matches:
        question_number, question, hint1, hint2, hint3 = match
        hints = [hint1, hint2, hint3]
        hint = next((h.strip() for h in hints if h), 'No hint provided')

        questions_dict[f"Q{question_number}"] = [question.strip(), hint]

    return questions_dict
if __name__ == "__main__":
    # Parsing the response
    questions_dictionary = parse_questions('response')

    # Printing the dictionary to check output
    print(questions_dictionary)