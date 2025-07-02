import os
from flask import Flask, render_template, request, send_file, redirect, url_for
import yt_dlp
import imageio_ffmpeg
import uuid

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Helper functions

def download_audio_as_mp3(url, output_path):
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'}
        ],
        'prefer_ffmpeg': True,
        'ffmpeg_location': ffmpeg_path,
        'quiet': True,
        'noplaylist': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        filename = os.path.splitext(filename)[0] + '.mp3'
    return filename

def download_video_as_mp4(url, output_path):
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'prefer_ffmpeg': True,
        'ffmpeg_location': ffmpeg_path,
        'quiet': True,
        'noplaylist': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        filename = os.path.splitext(filename)[0] + '.mp4'
    return filename

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        url = request.form.get('url')
        fmt = request.form.get('format')
        if not url or fmt not in ['mp3', 'mp4']:
            error = 'Please provide a valid URL and format.'
        else:
            try:
                # Use a unique subfolder for each download to avoid filename collisions
                session_id = str(uuid.uuid4())
                session_folder = os.path.join(DOWNLOAD_FOLDER, session_id)
                os.makedirs(session_folder, exist_ok=True)
                if fmt == 'mp3':
                    file_path = download_audio_as_mp3(url, session_folder)
                else:
                    file_path = download_video_as_mp4(url, session_folder)
                filename = os.path.basename(file_path)
                return send_file(file_path, as_attachment=True, download_name=filename)
            except Exception as e:
                error = f"Error: {str(e)}"
    return render_template('index.html', error=error)

if __name__ == '__main__':
    app.run(debug=True)
