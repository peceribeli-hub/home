import re

with open('api/index.py', 'r') as f:
    text = f.read()

bad_script = """<script>
    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }
    function toggleTheme() {
        const current = localStorage.getItem('theme') || 'dark';
        setTheme(current === 'dark' ? 'light' : 'dark');
    }
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
</script>"""

good_script = """<script>
    function setTheme(theme) {{
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }}
    function toggleTheme() {{
        const current = localStorage.getItem('theme') || 'dark';
        setTheme(current === 'dark' ? 'light' : 'dark');
    }}
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
</script>"""

text = text.replace(bad_script, good_script)

# Remove the duplicate script in the login page
duplicate = good_script + "\n\n" + good_script
text = text.replace(duplicate, good_script)

with open('api/index.py', 'w') as f:
    f.write(text)
