from flask import Flask, request, redirect, jsonify, render_template_string
import hashlib
import json
import os

app = Flask(__name__)

# Simple in-memory storage (will be lost on restart)
url_store = {}
DATA_FILE = 'data/urls.json'

# Load existing URLs if file exists
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, 'r') as f:
            url_store = json.load(f)
    except:
        url_store = {}

def save_urls():
    """Save URLs to file for persistence"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(url_store, f)

def generate_short_code(url):
    """Generate a short code from URL using hash"""
    return hashlib.md5(url.encode()).hexdigest()[:6]

# Simple HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Simple URL Shortener</title>
    <style>
        body { font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; }
        input, button { padding: 10px; margin: 5px; }
        input[type="url"] { width: 400px; }
        .result { background: #f0f0f0; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>🔗 Simple URL Shortener</h1>
    
    <form method="POST" action="/shorten">
        <input type="url" name="url" placeholder="Enter URL to shorten" required>
        <button type="submit">Shorten</button>
    </form>
    
    <h3>How to use:</h3>
    <p>1. Enter a URL above and click "Shorten"</p>
    <p>2. Get your short URL</p>
    <p>3. Use the short URL to redirect to the original</p>
    
    <h3>API:</h3>
    <p><code>POST /shorten</code> - with JSON: {"url": "https://example.com"}</p>
    <p><code>GET /{short_code}</code> - redirects to original URL</p>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/shorten', methods=['POST'])
def shorten_url():
    # Handle both form data and JSON
    if request.is_json:
        data = request.get_json()
        url = data.get('url')
    else:
        url = request.form.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Add http:// if no protocol specified
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    short_code = generate_short_code(url)
    url_store[short_code] = url
    save_urls()
    
    short_url = f"http://localhost:8080/{short_code}"
    
    if request.is_json:
        return jsonify({
            'original_url': url,
            'short_url': short_url,
            'short_code': short_code
        })
    else:
        return f'''
        <html>
        <body style="font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px;">
            <h2>✅ URL Shortened!</h2>
            <div style="background: #f0f0f0; padding: 15px; margin: 10px 0;">
                <p><strong>Original:</strong> {url}</p>
                <p><strong>Short URL:</strong> <a href="{short_url}" target="_blank">{short_url}</a></p>
            </div>
            <a href="/">← Back to home</a>
        </body>
        </html>
        '''

@app.route('/<short_code>')
def redirect_url(short_code):
    url = url_store.get(short_code)
    if url:
        return redirect(url)
    else:
        return jsonify({'error': 'Short URL not found'}), 404

@app.route('/stats')
def stats():
    return jsonify({
        'total_urls': len(url_store),
        'urls': url_store
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
