from flask import Flask, request, jsonify
import yt_dlp
import subprocess

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/get_mp3', methods=['POST'])
def get_mp3():
    data = request.json
    youtube_id = data.get("youtubeId")
    
    if not youtube_id:
        return jsonify({"error": "YouTube ID is required"}), 400
    try:
        # Set yt-dlp options to simulate the download and avoid downloading files
        ydl_opts = {
            'quiet': True,  # Suppress output
            'simulate': True  # Simulate download (don't actually download files)
        }

        # Initialize yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract the video info using the video ID
            info = ydl.extract_info(f'https://www.youtube.com/watch?v={youtube_id}', download=False)
        
        # Initialize m4a_url to None
        m4a_url = None
        
        # Loop through formats and find the m4a format
        for fmt in info.get('formats', []):
            if fmt['ext'] == 'm4a':
                m4a_url = fmt.get('url')
                break  # Stop after finding the first m4a format

        # Check if m4a format was found
        if m4a_url:
            return jsonify({"link": m4a_url})
        else:
            return jsonify({"error": "No m4a format available"}), 404

    except Exception as e:
        # Handle any exceptions and return the error message
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['GET'])
def search_video():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "Please provide a search query."}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,  # Fetch minimal info without resolving formats
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Fetch search results
            info = ydl.extract_info(f'ytsearch10:{query}', download=False)

        videos = []
        for entry in info.get('entries', []):
            video = {
                'id': entry.get('id'),
                'title': entry.get('title'),
                'artist': entry.get('channel'),
                'artwork': entry.get('thumbnail', f"https://i.ytimg.com/vi/{entry['id']}/hqdefault.jpg")
            }
            videos.append(video)

        return jsonify(videos)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=False)
