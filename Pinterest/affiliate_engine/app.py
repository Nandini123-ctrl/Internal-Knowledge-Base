from flask import Flask, render_template, request, jsonify
import sqlite3
import datetime
import re

app = Flask(__name__)
DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            amazon_url TEXT,
            affiliate_tag TEXT,
            affiliate_url TEXT,
            linktree_slug TEXT,
            pin_title TEXT,
            pin_description TEXT,
            pin_hashtags TEXT,
            yt_title TEXT,
            yt_script TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def build_affiliate_link(url, tag):
    # Appends or replaces the tag parameter in Amazon URLs
    clean_tag = tag.strip() if tag else "yourtag-20"
    if "tag=" in url:
        return re.sub(r'tag=[^&]+', f'tag={clean_tag}', url)
    elif "?" in url:
        return f"{url}&tag={clean_tag}"
    else:
        return f"{url}?tag={clean_tag}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate-campaign', methods=['POST'])
def generate_campaign():
    data = request.json
    prod_name = data.get('productName', 'Must-Have Tech Gadget').strip()
    raw_url = data.get('amazonUrl', '').strip()
    tag = data.get('affiliateTag', 'mypinterest-20').strip()
    category = data.get('category', 'Home & Kitchen').strip()

    # Generate Amazon Affiliate Link
    affiliate_url = build_affiliate_link(raw_url, tag)
    
    # Generate Linktree-style redirect slug
    slug_name = re.sub(r'[^a-zA-Z0-9]', '-', prod_name.lower())
    linktree_slug = f"linktr.ee/yourprofile/{slug_name[:25]}"

    # Copy Templates for Pinterest
    pin_title = f"10/10 Highly Rated {prod_name} You Need in 2026! ✨"
    pin_description = f"Transform your daily routine with the {prod_name}! Perfect for {category} lovers. Tap the link to check current price and discounts on Amazon."
    pin_hashtags = f"#{category.replace(' ', '')} #AmazonFinds #PinterestMadeMeBuyIt #AmazonAffiliate #HomeEssentials"

    # Copy Templates for YouTube Shorts / Reels
    yt_title = f"Unboxing the viral {prod_name}! 😱 #AmazonFinds"
    yt_script = f"[0-3s] Stop scrolling! If you love {category}, you need to see this.\n[3-10s] Show close-up of {prod_name} in use.\n[10-15s] It saves time and looks super aesthetic.\n[15-20s] Click the link in my Linktree / Bio to get yours on Amazon!"

    campaign_payload = {
        "productName": prod_name,
        "amazonUrl": raw_url,
        "affiliateUrl": affiliate_url,
        "linktreeSlug": linktree_slug,
        "pinTitle": pin_title,
        "pinDescription": pin_description,
        "pinHashtags": pin_hashtags,
        "ytTitle": yt_title,
        "ytScript": yt_script
    }

    return jsonify({"status": "success", "campaign": campaign_payload})

@app.route('/api/save-campaign', methods=['POST'])
def save_campaign():
    data = request.json
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO campaigns (
                product_name, amazon_url, affiliate_tag, affiliate_url, 
                linktree_slug, pin_title, pin_description, pin_hashtags, 
                yt_title, yt_script, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['productName'], data['amazonUrl'], data['affiliateTag'], data['affiliateUrl'],
            data['linktreeSlug'], data['pinTitle'], data['pinDescription'], data['pinHashtags'],
            data['ytTitle'], data['ytScript'], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Campaign saved to database!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # threaded=True prevents browser connection hangs
    app.run(host='127.0.0.1', port=3000, debug=False, threaded=True)
