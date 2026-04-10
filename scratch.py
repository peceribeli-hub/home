import re

with open('api/index.py', 'r') as f:
    text = f.read()

# Replace Login :root
login_root = """        :root {
            --bg-master: #050505;
            --brand-color: rgb(37, 99, 235);
            --card-bg: #090909;
            --text-white: #FFFFFF;
            --text-gray-light: #CCCCCC;
            --border-color: rgba(255, 255, 255, 0.1);
            --input-bg: #0A0A0A;
        }
        [data-theme="light"] {
            --bg-master: #F3F4F6;
            --card-bg: #FFFFFF;
            --text-white: #111827;
            --text-gray-light: #4B5563;
            --border-color: rgba(0, 0, 0, 0.1);
            --input-bg: #FFFFFF;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: var(--bg-master);"""

text = re.sub(r':root \{\s*--bg-master-dark: #050505;\s*--brand-color: rgb\(37, 99, 235\);\s*--card-bg: #090909;\s*--text-white: #FFFFFF;\s*--text-gray-light: #CCCCCC;\s*\}\s*\* \{ box-sizing: border-box; margin: 0; padding: 0; \}\s*body \{\s*background-color: var\(--bg-master-dark\);', login_root, text, count=1)

# Fix Login hardcoded colors
text = text.replace('background: #0A0A0A;', 'background: var(--input-bg);', 1)
text = text.replace('border: 1px solid rgba(255, 255, 255, 0.1);', 'border: 1px solid var(--border-color);', 2)

# Session :root
session_root = """        :root {
            --bg-master: #050505;
            --brand-color: rgb(37, 99, 235);
            --brand-color-dark: rgb(29, 78, 216);
            --card-bg: #090909;
            --text-white: #FFFFFF;
            --text-gray-light: #CCCCCC;
            --text-gray-dark: #666666;
            --border-color: rgba(255, 255, 255, 0.1);
            --border-dim: rgba(255, 255, 255, 0.05);
            --section-bg: #0A0A0A;
            --section-hover: #0D0D0D;
            --font-main: 'Inter', sans-serif;
        }
        [data-theme="light"] {
            --bg-master: #F3F4F6;
            --card-bg: #FFFFFF;
            --text-white: #111827;
            --text-gray-light: #4B5563;
            --text-gray-dark: #9CA3AF;
            --border-color: rgba(0, 0, 0, 0.1);
            --border-dim: rgba(0, 0, 0, 0.05);
            --section-bg: #F9FAFB;
            --section-hover: #F3F4F6;
        }
        body {
            background-color: var(--bg-master);"""

text = re.sub(r':root \{\s*--bg-master-dark: #050505;\s*--brand-color: rgb\(37, 99, 235\);\s*--brand-color-dark: rgb\(29, 78, 216\);\s*--card-bg: #090909;\s*--text-white: #FFFFFF;\s*--text-gray-light: #CCCCCC;\s*--text-gray-dark: #666666;\s*--font-main: \'Inter\', sans-serif;\s*\}\s*body \{\s*background-color: var\(--bg-master-dark\);', session_root, text, count=1)

# Replace all hardcoded styling in session/report
text = text.replace('rgba(255, 255, 255, 0.1)', 'var(--border-color)')
text = text.replace('rgba(255, 255, 255, 0.05)', 'var(--border-dim)')
text = text.replace('rgba(255, 255, 255, 0.2)', 'var(--border-color)')
text = text.replace('rgba(255,255,255,0.1)', 'var(--border-color)')
text = text.replace('#0A0A0A', 'var(--section-bg)')
text = text.replace('#0D0D0D', 'var(--section-hover)')
text = text.replace('#090909', 'var(--card-bg)')

# JS Theme logic globally
js_logic = """
<script>
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
</script>
"""

# inject in login
text = text.replace('<div class="login-container">', '<button class="theme-toggle" onclick="toggleTheme()" style="position:fixed; top:20px; right:20px; background:var(--card-bg); border:1px solid var(--border-color); color:var(--text-white); padding:10px; border-radius:50%; cursor:pointer; width:40px; height:40px; display:flex; align-items:center; justify-content:center; transition:0.3s; font-size:20px;" title="Modo Escuro/Claro">🌓</button>\n    <div class="login-container">', 1)
login_end = '</body>\n</html>'
if login_end in text:
    text = text.replace(login_end, js_logic + '</body>\n</html>', 1)

# inject in session
session_toggle = '<button class="theme-toggle" onclick="toggleTheme()" title="Modo Escuro/Claro" style="background:transparent; border:1px solid var(--border-color); color:var(--text-gray-light); border-radius:6px; cursor:pointer; display:flex; align-items:center; justify-content:center; height:36px; width:36px; transition:all 0.3s; font-size:16px;">🌓</button>\n            <button class="btn-refresh"'
text = text.replace('<button class="btn-refresh"', session_toggle)

# session JS is injected at the end before </body>
session_end = '</body>\n</html>\'\'\''
if session_end in text:
    text = text.replace(session_end, js_logic + '</body>\n</html>\'\'\'', 1)

with open('api/index.py', 'w') as f:
    f.write(text)

print("Replaced CSS variables and injected JS logic gracefully.")
