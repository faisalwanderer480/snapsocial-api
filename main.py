from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "SnapSocial API is Live!"

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"status": "error", "message": "No URL provided"}), 400

    # Google Play Policy: Blocking YouTube
    if "youtube.com" in video_url or "youtu.be" in video_url:
        return jsonify({
            "status": "error", 
            "message": "YouTube downloads are not supported to comply with Play Store policies."
        }), 400

    try:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_check_certificate': True,
            'cachedir': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return jsonify({
                "status": "success",
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "download_url": info.get('url'),
                "platform": info.get('extractor_key')
            })
    except Exception as e:
        return jsonify({"status": "error", "message": "Could not fetch video. Please check the link."}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
