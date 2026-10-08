import re

# Read the file
with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace conn.execute with cur.execute
content = content.replace('conn.execute(', 'cur.execute(')

# Add cur = conn.cursor() after each conn = get_connection()
content = re.sub(
    r'(conn = get_connection\(\))',
    r'\1\n    cur = conn.cursor()',
    content
)

# Write back
with open('streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed all conn.execute() to use cursor")
