from flask import Flask, request, jsonify
from functools import lru_cache
import yt_dlp
import os
import time

app = Flask(__name__)

# Basic In-Memory Cache (Stores 500 recent links for 1 hour to save CPU/Bandwidth)
CACHE = {}
CACHE_TTL = 3600  # 1 hour

def get_from_cache(url):
    if url in CACHE:
        data, timestamp = CACHE[url]
        if time.time() - timestamp < CACHE_TTL:
            return data
        else:
            del CACHE[url]
    return None

def set_to_cache(url, data):
    if len(CACHE) > 500: # Cache full hoye gele oldest clear kora
        CACHE.clear()
        
    CACHE[url] = (data, time.time())

@app.route('/')
def home():
    return jsonify({"status": "success", "message": "SnapSocial Engine v2.0 Active"}), 200

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({"status": "error", "message": "No URL provided"}), 400

    clean_url = video_url.strip()
    clean_url_lower = clean_url.lower()

    # 1. Play Store Policy Protection (YouTube Ban)
    youtube_domains = ['youtube.com', 'youtu.be', 'youtube-nocookie.com', 'm.youtube.com']
    if any(domain in clean_url_lower for domain in youtube_domains):
        return jsonify({
            "status": "error", 
            "message": "YouTube downloads are disabled to comply with Play Store policies."
        }), 400

    # 2. Check Cache
    cached_response = get_from_cache(clean_url)
    if cached_response:
        cached_response['cached'] = True
        return jsonify(cached_response), 200

    try:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'no_check_certificate': True,
            'cachedir': False,
            'noplaylist': True,
            'socket_timeout': 10,
            
            # --- PRODUCTION ADVANCED SETTINGS ---
            # 1. Cookies file (Instagram/FB issue fix korar jonno):
            # 'cookiefile': 'cookies.txt', 

            # 2. Proxy Support (Jodi IP Block hoy, proxy enable korbe):
            # 'proxy': os.environ.get('PROXY_URL'), # Example: http://user:pass@proxy_ip:port

            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(clean_url, download=False)

            download_url = info.get('url')
            
            # Fallback format checking
            if not download_url and 'formats' in info:
                formats = info.get('formats', [])
                valid_mp4s = [f for f in formats if f.get('url') and f.get('ext') == 'mp4']
                if valid_mp4s:
                    download_url = valid_mp4s[-1].get('url')
                elif formats:
                    download_url = formats[-1].get('url')

            if not download_url:
                return jsonify({
                    "status": "error", 
                    "message": "Direct stream link missing or content is private."
                }), 422

            result = {
                "status": "success",
                "title": info.get('title', 'Social Media Media'),
                "thumbnail": info.get('thumbnail'),
                "download_url": download_url,
                "platform": info.get('extractor_key', 'Unknown'),
                "duration": info.get('duration'),
                "cached": False
            }

            # Save to Cache
            set_to_cache(clean_url, result)

            return jsonify(result), 200

    except Exception as e:
        error_msg = str(e)
        print(f"[Error Log]: {error_msg}")
        
        return jsonify({
            "status": "error", 
            "message": "Failed to extract media. Link might be private or unsupported."
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)















# from flask import Flask, request, jsonify
# import yt_dlp
# import os

# app = Flask(__name__)

# @app.route('/')
# def home():
#     return "SnapSocial API is Live!"

# @app.route('/download', methods=['GET'])
# def download():
#     video_url = request.args.get('url')
#     if not video_url:
#         return jsonify({"status": "error", "message": "No URL provided"}), 400

#     # Google Play Policy: Blocking YouTube
#     if "youtube.com" in video_url or "youtu.be" in video_url:
#         return jsonify({
#             "status": "error", 
#             "message": "YouTube downloads are not supported to comply with Play Store policies."
#         }), 400

#     try:
#         ydl_opts = {
#             'format': 'best',
#             'quiet': True,
#             'no_check_certificate': True,
#             'cachedir': False,
#         }
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(video_url, download=False)
#             return jsonify({
#                 "status": "success",
#                 "title": info.get('title'),
#                 "thumbnail": info.get('thumbnail'),
#                 "download_url": info.get('url'),
#                 "platform": info.get('extractor_key')
#             })
#     except Exception as e:
#         return jsonify({"status": "error", "message": "Could not fetch video. Please check the link."}), 500

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host='0.0.0.0', port=port)
