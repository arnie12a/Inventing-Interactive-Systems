
from pathlib import Path
from uuid import uuid4
import yt_dlp


def download_audio(url, output_dir="audio_samples"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    unique_id = uuid4().hex

    options = {
        "format": "bestaudio/best",
        "outtmpl": str(
            output_dir / f"%(id)s_{unique_id}.%(ext)s"
        ),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
        }],
        "noplaylist": True,
        "overwrites": False,
        "continuedl": False,
        "quiet": False,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)

    video_id = info["id"]
    audio_path = output_dir / f"{video_id}_{unique_id}.wav"

    if not audio_path.exists():
        raise RuntimeError("Audio download failed")

    return audio_path, video_id
