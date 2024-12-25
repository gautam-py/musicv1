from flask import Flask, request, jsonify
import yt_dlp
import subprocess

app = Flask(__name__)

@app.route('/get_audio', methods=['GET'])
def get_audio():
    # Get the YouTube video ID from the request
    video_id = request.args.get('video_id', '')
    
    # Check if the video_id is provided
    if not video_id:
        return jsonify({"error": "Please provide a video ID."}), 400

    try:
        # Set yt-dlp options to simulate the download and avoid downloading files
        ydl_opts = {
            'quiet': True,  # Suppress output
            'simulate': True,  # Simulate download (don't actually download files)
            'cookies-from-browser': 'chrome'  # Automatically extract cookies from Chrome
        }

        # Initialize yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract the video info using the video ID
            info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
        
        # Initialize m4a_url to None
        m4a_url = None
        
        # Loop through formats and find the m4a format
        for fmt in info.get('formats', []):
            if fmt['ext'] == 'm4a':
                m4a_url = fmt.get('url')
                break  # Stop after finding the first m4a format

        # Check if m4a format was found
        if m4a_url:
            return jsonify({'m4a_url': m4a_url})
        else:
            return jsonify({"error": "No m4a format available"}), 404

    except Exception as e:
        # Handle any exceptions and return the error message
        return jsonify({"error": str(e)}), 500
    
@app.route('/search', methods=['GET'])
def search_video():
    # Get the search query from the request
    query = request.args.get('query', '')
    
    # Check if the query is empty
    if not query:
        return jsonify({"error": "Please provide a search query."}), 400

    try:
        # Set yt-dlp options to simulate a search and avoid downloading the video
        ydl_opts = {
            'quiet': True,  # Suppress output
            'simulate': True,  # Simulate download (don't actually download files)
            'cookies-from-browser': 'chrome'  # Automatically extract cookies from Chrome
        }
        
        # Initialize yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info using the search query
            info = ydl.extract_info(f'ytsearch:{query}', download=False)
        
        # List to store the found videos
        videos = []
        
        # Loop through the search results
        for item in info.get('entries', []):
            # Initialize the m4a_url to None
            m4a_url = None
            
            # Find the first available m4a format
            for fmt in item.get('formats', []):
                if fmt['ext'] == 'm4a':
                    m4a_url = fmt.get('url')
                    break  # Stop once the first m4a format is found

            # If m4a format is found, create a video entry
            if m4a_url:
                video = {
                    'id': item['id'],
                    'title': item['title'],
                    'description': item['description'],
                    'm4a_url': m4a_url  # Provide the direct m4a URL
                }
            else:
                # Handle cases where no m4a format is available
                video = {
                    'id': item['id'],
                    'title': item['title'],
                    'description': item['description'],
                    'm4a_url': "No m4a available"
                }
            
            videos.append(video)

        # Return the list of videos in JSON format
        return jsonify(videos)

    except Exception as e:
        # Handle any exceptions that might occur
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)
