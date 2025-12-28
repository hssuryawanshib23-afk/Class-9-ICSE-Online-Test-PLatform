import re

# Read the file
with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the malformed cursor lines with literal backtick-r-backtick-n
content = re.sub(r'`r`n\s*cur = conn\.cursor\(\)', '', content)

# Ensure there's exactly one cur = conn.cursor() after each conn = get_connection()
# First, remove any existing cur = conn.cursor() lines
content = re.sub(r'\n\s*cur = conn\.cursor\(\)', '', content)

# Then add them back properly after each get_connection()
content = re.sub(
    r'(conn = get_connection\(\))',
    r'\1\n    cur = conn.cursor()',
    content
)

# Write back
with open('streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed streamlit_app.py")

# Now fix generate_test_engine.py
with open('generate_test_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Check if it needs cursor fix
if 'cur = conn.cursor()' not in content:
    content = re.sub(
        r'(conn = get_connection\(\))',
        r'\1\n    cur = conn.cursor()',
        content
    )
    with open('generate_test_engine.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Fixed generate_test_engine.py")
else:
    print("✅ generate_test_engine.py already correct")

print("\n✅ All files fixed!")
