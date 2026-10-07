from flask import Flask, render_template_string, request
import webbrowser
from threading import Timer

app = Flask(__name__)

documents = [
    {"category": "HR & Finance", "title": "Submitting Expense Reports", "summary": "Step-by-step guide on how to submit monthly business expenses and claim reimbursement."},
    {"category": "HR & Finance", "title": "Company Holiday Calendar 2026", "summary": "List of official public holidays, optional leaves, and company shutdown days for 2026."},
    {"category": "IT Support", "title": "How to Connect to Office Wi-Fi", "summary": "Instructions for connecting your laptop and mobile devices to the secure corporate wireless network."},
    {"category": "IT Support", "title": "VPN Setup Guide", "summary": "Guidelines on installing and configuring the secure remote-access VPN client."},
    {"category": "Operations", "title": "Security Guidelines & Password Policy", "summary": "Standard operating procedures for maintaining account security and multi-factor authentication."}
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Internal Knowledge Base</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f8f9fa; margin: 0; padding: 20px; color: #333; }
        .header { background: #fff; padding: 15px; border-bottom: 1px solid #e1e4e8; display: flex; justify-content: space-between; }
        .hero { text-align: center; padding: 30px; }
        .search-box { display: inline-flex; width: 100%; max-width: 600px; background: #fff; border: 1px solid #d1d5da; border-radius: 6px; overflow: hidden; }
        .search-box input { flex: 1; padding: 12px; border: none; outline: none; }
        .search-box button { background: #0366d6; color: white; border: none; padding: 0 20px; cursor: pointer; }
        .content { max-width: 800px; margin: 0 auto; }
        .doc-item { background: #fff; padding: 15px; border: 1px solid #e1e4e8; border-radius: 6px; margin-bottom: 15px; }
        .badge { display: inline-block; padding: 3px 8px; font-size: 11px; font-weight: bold; color: #fff; background: #0366d6; border-radius: 4px; margin-bottom: 8px; }
    </style>
</head>
<body>
    <div class="header">
        <h1 style="font-size:16px; color:#0366d6; margin:0;">Team Portal: Knowledge Base</h1>
        <a href="/" style="text-decoration:none; color:#586069;">Home</a>
    </div>
    <div class="hero">
        <h2>How can we help you today?</h2>
        <form class="search-box" method="POST" action="/">
            <input type="text" name="query" value="{{ query }}" placeholder="Search policies, Wi-Fi, HR guidelines...">
            <button type="submit">Search</button>
        </form>
    </div>
    <div class="content">
        <h3>Documents</h3>
        {% if documents %}
            {% for doc in documents %}
                <div class="doc-item">
                    <span class="badge">{{ doc.category }}</span>
                    <a href="#" style="display:block; font-size:16px; color:#0366d6; text-decoration:none; font-weight:bold; margin-bottom:5px;">{{ doc.title }}</a>
                    <p style="font-size:14px; color:#586069; margin:0;">{{ doc.summary }}</p>
                </div>
            {% endfor %}
        {% else %}
            <p style="color: #586069;">No documents found matching your search.</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    query = ""
    results = documents
    if request.method == 'POST':
        query = request.form.get('query', '')
        if query:
            results = [doc for doc in documents if query.lower() in doc['title'].lower() or query.lower() in doc['summary'].lower()]
    return render_template_string(HTML_TEMPLATE, documents=results, query=query)

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(debug=True, port=5000)
