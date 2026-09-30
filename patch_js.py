html_file = "src/ControlService/wwwroot/index.html"
with open(html_file, "r") as f:
    content = f.read()

old_fetch = """            const res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });"""

new_fetch = """            const req = { method: 'POST' };
            if (Object.keys(body).length > 0) {
                req.headers = { 'Content-Type': 'application/json' };
                req.body = JSON.stringify(body);
            }
            const res = await fetch(url, req);"""

content = content.replace(old_fetch, new_fetch)
with open(html_file, "w") as f:
    f.write(content)

