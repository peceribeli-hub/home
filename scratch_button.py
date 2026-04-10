import traceback

try:
    with open('api/index.py', 'r') as f:
        text = f.read()

    # 1. Fix the CSS logic in get_login_page
    old_login_root = """        :root {{
            --bg-master-dark: #050505;
            --brand-color: rgb(37, 99, 235);
            --card-bg: var(--card-bg);
            --text-white: #FFFFFF;
            --text-gray-light: #CCCCCC;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-master-dark);"""

    new_login_root = """        :root {{
            --bg-master: #050505;
            --brand-color: rgb(37, 99, 235);
            --card-bg: #090909;
            --input-bg: #0A0A0A;
            --text-white: #FFFFFF;
            --text-gray-light: #CCCCCC;
            --text-gray-dark: #666666;
            --border-color: rgba(255, 255, 255, 0.1);
        }}
        [data-theme="light"] {{
            --bg-master: #F3F4F6;
            --card-bg: #FFFFFF;
            --input-bg: #FFFFFF;
            --text-white: #111827;
            --text-gray-light: #4B5563;
            --text-gray-dark: #9CA3AF;
            --border-color: rgba(0, 0, 0, 0.1);
        }}
        .theme-text::after {{ content: "Modo claro"; }}
        .icon-sun {{ display: block; fill: currentColor; width: 16px; height: 16px; }}
        .icon-moon {{ display: none; fill: currentColor; width: 16px; height: 16px; }}
        [data-theme="light"] .theme-text::after {{ content: "Modo escuro"; }}
        [data-theme="light"] .icon-sun {{ display: none; }}
        [data-theme="light"] .icon-moon {{ display: block; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-master);"""

    if old_login_root not in text: print("Could not find old_login_root")
    text = text.replace(old_login_root, new_login_root)

    # 2. Fix the CSS logic in get_session_page
    old_session_root = """        :root {{
            --bg-master-dark: #050505;
            --brand-color: rgb(37, 99, 235);
            --brand-color-dark: rgb(29, 78, 216);
            --card-bg: var(--card-bg);
            --text-white: #FFFFFF;
            --text-gray-light: #CCCCCC;
            --text-gray-dark: #666666;
            --font-main: 'Inter', sans-serif;
        }}
        body {{
            background-color: var(--bg-master-dark);"""

    new_session_root = """        :root {{
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
        }}
        [data-theme="light"] {{
            --bg-master: #F3F4F6;
            --card-bg: #FFFFFF;
            --text-white: #111827;
            --text-gray-light: #4B5563;
            --text-gray-dark: #9CA3AF;
            --border-color: rgba(0, 0, 0, 0.1);
            --border-dim: rgba(0, 0, 0, 0.05);
            --section-bg: #F9FAFB;
            --section-hover: #F3F4F6;
        }}
        .theme-text::after {{ content: "Modo claro"; }}
        .icon-sun {{ display: block; fill: currentColor; width: 14px; height: 14px; }}
        .icon-moon {{ display: none; fill: currentColor; width: 14px; height: 14px; }}
        [data-theme="light"] .theme-text::after {{ content: "Modo escuro"; }}
        [data-theme="light"] .icon-sun {{ display: none; }}
        [data-theme="light"] .icon-moon {{ display: block; }}
        body {{
            background-color: var(--bg-master);"""

    if old_session_root not in text: print("Could not find old_session_root")
    text = text.replace(old_session_root, new_session_root)

    # 3. Replace Button in get_login_page
    old_login_btn = '<button class="theme-toggle" onclick="toggleTheme()" style="position:fixed; top:20px; right:20px; background:var(--card-bg); border:1px solid var(--border-color); color:var(--text-white); padding:10px; border-radius:50%; cursor:pointer; width:40px; height:40px; display:flex; align-items:center; justify-content:center; transition:0.3s; font-size:20px;" title="Modo Escuro/Claro">🌓</button>'
    new_login_btn = '<button class="theme-toggle" onclick="toggleTheme()" style="position:fixed; top:24px; right:24px; background:var(--card-bg); border:1px solid var(--border-color); color:var(--text-gray-light); padding:8px 16px; border-radius:8px; cursor:pointer; display:flex; align-items:center; gap:8px; transition:0.3s; font-family:\'Inter\',sans-serif; font-size:13px; font-weight:600;"><svg class="icon-sun" viewBox="0 0 24 24"><path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"/></svg><svg class="icon-moon" viewBox="0 0 24 24"><path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-3.03 0-5.5-2.47-5.5-5.5 0-1.82.89-3.42 2.26-4.4C12.92 3.04 12.46 3 12 3zm0 16c-3.86 0-7-3.14-7-7s3.14-7 7-7c.18 0 .35.02.52.05-.2.85-.31 1.74-.31 2.66 0 4.15 2.65 7.68 6.44 8.78-1.92 1.58-4.28 2.51-6.65 2.51z"/></svg><span class="theme-text"></span></button>'
    
    if old_login_btn not in text: print("Could not find old_login_btn")
    text = text.replace(old_login_btn, new_login_btn)

    # 4. Replace Button in get_session_page
    old_session_btn = '<button class="theme-toggle" onclick="toggleTheme()" title="Modo Escuro/Claro" style="background:transparent; border:1px solid var(--border-color); color:var(--text-gray-light); border-radius:6px; cursor:pointer; display:flex; align-items:center; justify-content:center; height:36px; width:36px; transition:all 0.3s; font-size:16px;">🌓</button>'
    new_session_btn = '<button class="theme-toggle" onclick="toggleTheme()" style="background:transparent; border:1px solid var(--border-color); color:var(--text-gray-light); padding:0 12px; border-radius:6px; cursor:pointer; display:flex; align-items:center; gap:8px; height:36px; transition:all 0.3s; font-family:\'Inter\',sans-serif; font-size:13px; font-weight:600;"><svg class="icon-sun" viewBox="0 0 24 24"><path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"/></svg><svg class="icon-moon" viewBox="0 0 24 24"><path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-3.03 0-5.5-2.47-5.5-5.5 0-1.82.89-3.42 2.26-4.4C12.92 3.04 12.46 3 12 3zm0 16c-3.86 0-7-3.14-7-7s3.14-7 7-7c.18 0 .35.02.52.05-.2.85-.31 1.74-.31 2.66 0 4.15 2.65 7.68 6.44 8.78-1.92 1.58-4.28 2.51-6.65 2.51z"/></svg><span class="theme-text"></span></button>'

    if old_session_btn not in text: print("Could not find old_session_btn")
    text = text.replace(old_session_btn, new_session_btn)

    with open('api/index.py', 'w') as f:
        f.write(text)
    
    print("Done")
except Exception as e:
    traceback.print_exc()
