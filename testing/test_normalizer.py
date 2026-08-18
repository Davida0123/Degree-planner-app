from ingest.prereq_parser import normalize_prereq_str as Preprocessor
NORMALIZER = Preprocessor
TEST_CASES = [
    # Shorthand & Slashes
    "CMPT 101, 103, or 200",
    "MATH 114 / 115 or 120 / 125",
    "STAT 151, 161, 252",
    
    # Grade Constraints
    "A minimum grade of C- in CMPT 101 or ENCP 100",
    "Minimum grade of C in CMPT 201, CMPT 204, and MATH 114",
    "CMPT 103 with a minimum grade of B and CMPT 200 with a minimum grade of C-",
    
    # Quantifiers & Disjunctions
    "One of CMPT 101, CMPT 103, or CMPT 114",
    "One of CMPT 101 or 103, and one of MATH 114 or 120",
    "Either CMPT 200 or CMPT 201, and STAT 151",
    
    # Compound & Delimiters
    "CMPT 201, CMPT 204; MATH 114 or MATH 125; and STAT 151",
    "CMPT 101 and CMPT 103 or CMPT 114 and CMPT 115",
    
    # Non-Standard & Mixed
    "Consent of department.",
    "A minimum grade of C- in CMPT 101 or ENCP 100 or three credits of intermediate CSE including CSE 2120.",
    "Admission to the Computing Science Major, and CMPT 200."
]

def run_tests(normalizer_func):
    for idx, test in enumerate(TEST_CASES, 1):
        print(f"--- Test {idx} ---")
        print(f"Raw:        {test}")
        print(f"Normalized: {normalizer_func(test)}\n")

if __name__ == "__main__":
    run_tests(NORMALIZER)