import re
import os

def parse_questions(content):
    lines = content.split('\n')
    questions = []
    current_q = {"text": [], "options": []}
    
    # Skip header if it exists
    start_idx = 0
    if len(lines) > 0 and lines[0].strip().startswith("#"):
        # Heuristic to skip header lines until "---"
        for i, line in enumerate(lines):
            if line.strip() == "---":
                start_idx = i + 1
                break
        else:
             start_idx = 3 # fall back if no separator found but # tag exists

    iterator = iter(lines[start_idx:])
    
    for line in iterator:
        stripped = line.strip()
        if not stripped:
            continue
            
        # Check if option (simple check for (A), (B), etc)
        # Also handles cases where options are on one line like (A)... (B)...
        # But for now assume one per line or strict split if needed?
        # The user provided text mostly has them on separate lines in the later part, 
        # but line 38: (A)...(B)... might need splitting?
        # Let's check line 38 in previously viewed content:
        # `38: (A)情同「手足」／「手足」無措` -> This looks like just (A). Wait.
        # Line 1-2 example:
        # `1: ...庾亮...`
        # `2: (A)...`
        # `3: (B)...`
        # This is clean.
        
        # What about: `20: (A)不到黃河心不死╱君子之交淡如水╱化干戈為玉帛`
        # This looks like one option (A) containing multiple phrases separated by slash.
        # It doesn't look like (A)... (B)... on same line.
        # So treating lines starting with (X) as options is safe.
        
        if re.match(r'^\([A-D]\)', stripped):
            current_q["options"].append(stripped)
        elif stripped.startswith("*"): # Footnote or similar
             current_q["text"].append(stripped)
        else:
            # If we already have options, this means a new question started
            if current_q["options"]:
                questions.append(current_q)
                current_q = {"text": [], "options": []}
            
            # Append to text
            current_q["text"].append(stripped)
            
    # Append last
    if current_q["text"] or current_q["options"]:
        questions.append(current_q)
        
    return questions

def format_questions(questions):
    output = []
    output.append("# 國語科題庫")
    output.append("")
    output.append("本題庫彙整自用戶提供。")
    output.append("")
    output.append("---")
    output.append("")
    
    for i, q in enumerate(questions, 1):
        output.append(f"### {i}.")
        # Join text lines
        text = "\n".join(q["text"])
        output.append(text)
        output.append("")
        
        # Options
        for opt in q["options"]:
            output.append(opt)
        
        output.append("") # Blank line after question
        
    return "\n".join(output)

file_path = '/Users/michael/mock_exam_tutor/exams/bank/chinese-gr6-bank.md'
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    questions = parse_questions(content)
    formatted = format_questions(questions)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(formatted)
        
    print(f"Successfully formatted {len(questions)} questions.")
except Exception as e:
    print(f"Error: {e}")
