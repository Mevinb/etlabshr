#!/usr/bin/env python3

def semester_matches(semester_text, requested_semester):
    """Helper function to match semester text with requested semester number"""
    if not semester_text:
        return False
    
    # If no specific semester requested, return all results
    if requested_semester is None:
        return True
        
    semester_mapping = {
        1: ["first", "1st", "i", "1"],
        2: ["second", "2nd", "ii", "2"],
        3: ["third", "3rd", "iii", "3", "IIIrd"],
        4: ["fourth", "4th", "iv", "4"],
        5: ["fifth", "5th", "v", "5"],
        6: ["sixth", "6th", "vi", "6"],
        7: ["seventh", "7th", "vii", "7"],
        8: ["eighth", "8th", "viii", "8"]
    }
    
    semester_text_lower = semester_text.lower()
    
    # Direct number match
    if str(requested_semester) in semester_text_lower:
        return True
    
    # Text-based matching
    if requested_semester in semester_mapping:
        for variant in semester_mapping[requested_semester]:
            if variant.lower() in semester_text_lower:
                return True
    
    # Debug message for unmatched semesters
    print(f"Debug: Semester text '{semester_text}' didn't match requested semester {requested_semester}")
    return False  # Only return matching semester results

# Test cases
test_cases = [
    ("IIIrd Semester", 3),
    ("IIIrd Semester", None),
    ("Third Semester", 3),
    ("1st Semester", 1),
    ("", 3),
    ("Random text", 3)
]

print("Testing semester matching function:")
print("=" * 50)

for semester_text, requested_semester in test_cases:
    result = semester_matches(semester_text, requested_semester)
    print(f"'{semester_text}' vs {requested_semester} -> {result}")