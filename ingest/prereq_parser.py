import re

#Handles parsing and assigning respective logic between courses(through string modification/clarification) 
def normalize_prereq_str(raw_txt: str) -> str:
    '''
    Preprocessor that normalizes passed prerequisite string to enhance reading and sorting of data
    Pre: raw_txt isnt empty
    '''

    text = raw_txt.strip()

    if not text or text.lower() == "n/a":
        return "N/A"

    # 1. Standardize slashes to ' or '
    text = re.sub(r'\s*/\s*', ' or ', text)

    # 2. Standardize Oxford commas and clean punctuation
    text = re.sub(r'\s*,\s*or\s+', ' or ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*,\s*and\s+', ' and ', text, flags=re.IGNORECASE)

    # 3. Forward-fill omitted department prefixes (e.g., "CMPT 101, 103, or 200")
    # Loops until all chained numbers inherit the preceding department
    dept_chain_pattern = r'([A-Z]{3,4})\s+(\d{3})((?:\s*(?:,|and|or)\s*\d{3})+)'
    #eg                      cmpt          103        ',' -> 'and' or 'or'   104
    #group i.e()               1            2          ignored            3
    def expand_chain(match):
        dept = match.group(1)
        first_num = match.group(2)
        rest = match.group(3)
        # Inject the department prefix before every isolated course number in the rest of the chain
        expanded_rest = re.sub(r'(\d{3})', rf'{dept} \1', rest)
        return f"{dept} {first_num}{expanded_rest}"

    text = re.sub(dept_chain_pattern, expand_chain, text, flags=re.IGNORECASE) #normalized

    # 4. Handle serial OR lists: if a list of courses ends in 'or', replace preceding commas with 'or'
    # Example: "CMPT 101, CMPT 103 or CMPT 200" -> "CMPT 101 or CMPT 103 or CMPT 200"
    serial_or_pattern = r'([A-Z]{3,4}\s+\d{3})\s*,\s*(?=[A-Z]{3,4}\s+\d{3}\s+or\b)'
    while re.search(serial_or_pattern, text, flags=re.IGNORECASE):
        text = re.sub(serial_or_pattern, r'\1 or ', text, flags=re.IGNORECASE)

    # 5. Remove quantifier phrasing ("one of", "any of", "either")
    text = re.sub(r'\b(one of|any of|either of|either)\b\s*', '', text, flags=re.IGNORECASE)

    # 6. Convert remaining standard commas between courses to 'and' (Implicit AND)
    text = re.sub(r'([A-Z]{3,4}\s+\d{3})\s*,\s*(?=[A-Z]{3,4}\s+\d{3})', r'\1 and ', text)

    # 7. Clean up extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text

#Grade Extraction
def extract_grade_requirements(text: str, default_grade: str = "D"): # D is minimum passing grade
    """
    Extracts explicit grade requirements from text and normalizes courses
    into a standardized format: (COURSE_CODE, MIN_GRADE).
    """
    cleaned_text = text.strip()
    # 1. Check for a Leading Grade Scope (e.g., "A minimum grade of C- in CMPT 101 or CMPT 103")
    leading_match = re.search(
        r'(?:a\s+)?(?:minimum\s+grade\s+of|grade\s+of\s+at\s+least|minimum)\s+([A-D][+-]?)\s+(?:in|for)\s+',
        cleaned_text,
        flags=re.IGNORECASE
    )
    
    active_scope_grade = default_grade
    if leading_match:
        active_scope_grade = leading_match.group(1).upper()
        # Strip off the leading phrase so only course logic remains
        cleaned_text = cleaned_text[:leading_match.start()] + cleaned_text[leading_match.end():]

    # 2. Tag Trailing Inline Grades (e.g., "CMPT 103 with a minimum grade of B")
    trailing_pattern = r'([A-Z]{3,4}\s+\d{3})\s+(?:with\s+(?:a\s+)?(?:minimum\s+)?grade\s+of\s+|with\s+)([A-D][+-]?)(?:\s+or\s+better)?'
    
    def tag_trailing(match):
        course = match.group(1).upper()
        grade = match.group(2).upper()
        return f"{course}__GRADE_{grade}__"

    cleaned_text = re.sub(trailing_pattern, tag_trailing, cleaned_text, flags=re.IGNORECASE)

    # 3. Tag Remaining Untagged Courses with the Active Scope Grade
    def tag_remaining(match):
        course = match.group(1).upper()
        return f"{course}__GRADE_{active_scope_grade}__"

    # Match courses that have not already been tagged with __GRADE_X__ with the default grade
    cleaned_text = re.sub(
        r'([A-Z]{3,4}\s+\d{3})(?!__GRADE_)',
        tag_remaining,
        cleaned_text
    )
    print(f'cleaned: {cleaned_text}') # debugg
    return cleaned_text.strip()

#Grade Tokenization
def make_course_node(token: str) -> dict:
    '''
    turns "CourseCode__GRADE_?__" into JSON format
    '''
    match = re.match(r'([A-Z]{3,4}\s+\d{3})__GRADE_([A-D][+-]?)__', token.strip())
    if match:
        return {
            "node_type": "COURSE_CHECK",
            "course_code": match.group(1),
            "min_grade": match.group(2)
        }
    return {
        "node_type": "MANUAL_APPROVAL",
        "raw_text": token.strip()
    }

#Logic Splitter
def split_at_top_level(text: str, delimiter_regex: str) -> list[str]:
    """
    splits an expression by a passed logical delimiter (like AND, OR, or ;) only when that operator is 
    outside of all parentheses.
    post: returns a list of course codes that can be easily parsed into json nested tree logic
    """
    parts = [] #result
    current = []
    depth = 0 #0->top level, > 0 means inside parenthesis
    i = 0
    pattern = re.compile(delimiter_regex, re.IGNORECASE) # compiling into a REGEX obj speeds up processing time

    while i < len(text):
        char = text[i]

        if char == '(':
            depth += 1
            current.append(char)
            i += 1
        elif char == ')':
            depth = max(0, depth - 1)
            current.append(char)
            i += 1
        elif depth == 0:
            # Check if a delimiter starts at the current index
            match = pattern.match(text[i:])
            if match: #if 'and','or',...
                parts.append("".join(current).strip()) #store left side of delimeter in parts
                current = []
                i += match.end() #move pointer passed operator
            else:
                current.append(char)
                i += 1
        else: # inside (), dont split, jsut collect characters to preserve presedence
            current.append(char)
            i += 1

    if current:
        parts.append("".join(current).strip()) #

    return [p for p in parts if p] # ['cmpt 103', 'cmpt 204']

if __name__ == "__main__":
    #extract_grade_requirements("STAT 151 and STAT 161",)