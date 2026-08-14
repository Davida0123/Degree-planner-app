import re

def normalize_prereq_str(raw_txt: str) -> str:
    '''
    Pre: raw_txt isnt empty
    '''

    text = raw_txt.strip()

    #match dep code + number followed by ','. i.e cmpt 101, 102, 104
    shorthand_pattern = r'([A-Z]{3,4})\s+(\d{3})\s*(?:,|/|and|or)\s*(\d{3})'
    #eg                     cmpt          103      ','or'/'or'and'or'or'  104  
    #group                  1              2         Not stored            3
    
### 
    while re.search(shorthand_pattern, text):
        text = re.sub(shorthand_pattern, r'\1 \2 and \1 \3', text) # backreference using groub 1,2 and 3 from shorthand_pattern
#                how do we know the operator here ^ is 'and' and not 'or'
    # 2. Check for Disjunction prefixes ("One of", "Either of")
    disjunction_prefixes = ["one of", "any of", "either of"]
    is_or_group = any(text.lower().startswith(prefix) for prefix in disjunction_prefixes)

    # Clean off the prefix phrase once identified
    for prefix in disjunction_prefixes:
        if text.lower().startswith(prefix):
            text = text[len(prefix):].strip(" :")

    # 3. Replace remaining commas between course codes with the appropriate operator
    replacement_op = " OR " if is_or_group else " AND "
    
    # Regex looks for a comma surrounded by course codes (e.g. "CMPT 101, CMPT 201")
    text = re.sub(r'(?<=[A-Z]{3,4}\s\d{3})\s*,\s*(?=[A-Z]{3,4}\s\d{3})', replacement_op, text)
    
    # Standardize Oxford commas (e.g., ", and" -> " AND ", ", or" -> " OR ")
    text = re.sub(r'\s*,\s*and\s+', ' AND ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s*,\s*or\s+', ' OR ', text, flags=re.IGNORECASE)

    return text
###