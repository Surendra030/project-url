# getaudio.py
import subprocess
import re
import os
def get_audio_streams(file_name):
    """
    Extract audio stream details from a media file using FFmpeg.
    
    Args:
        file_name (str): Path to the media file.
    
    Returns:
        list: A list of dictionaries containing audio stream details.
    """
    try:
        # Run the ffmpeg command and capture the output
        result = subprocess.run(
            ["./ffmpeg/ffmpeg",  # Use relative path to the FFmpeg binary in the repo

              "-i", file_name],
            stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True
        )
        output = result.stderr

        audio_streams = []
        with open("temp.txt","w",encoding='utf-8')as f:
            f.write(output)
        for line in output.splitlines():
            if "Audio" in line:
                # Extract stream index
                stream_match = re.search(r"Stream #(\d+:\d+)", line)
                stream_index = stream_match.group(1) if stream_match else None

                # Extract language (if available)
                lang_match = re.search(r"\((\w{3})\)", line)
                language = lang_match.group(1) if lang_match else "und"  # Default to 'und' (undefined)

                # Extract codec
                codec_match = re.search(r"Audio: (\w+)", line)
                codec = codec_match.group(1) if codec_match else "unknown"

                # Extract sample rate
                sample_rate_match = re.search(r"(\d+) Hz", line)
                sample_rate = int(sample_rate_match.group(1)) if sample_rate_match else None

                # Extract channel configuration
                channel_match = re.search(r", (\d+) channels", line)
                channels = int(channel_match.group(1)) if channel_match else None

                # Extract title (if available)
                title_match = re.search(r"title\s*:\s*(.+)", line, re.IGNORECASE)
                title = title_match.group(1).strip() if title_match else "No title"

                # Append parsed details
                audio_streams.append({
                    "index": stream_index,
                    "language": language,
                    "codec": codec,
                    "sample_rate": sample_rate,
                    "channels": channels,
                    "title": title
                })
        return audio_streams

    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def extract_audio(link_id,video_file, audio_streams):
    print("extracting audio ")
    """Extract audio streams from video file and save them to MP3 files."""
    for stream in audio_streams:
        stream_index = stream["index"]
        language = stream["language"]
        # Construct the output filename based on language or stream index
        output_filename = f"{link_id}_{language.lower()}.mp3" if language else f"output_{stream_index}.mp3"
        # Construct the ffmpeg command to extract audio
        command = [
            "./ffmpeg/ffmpeg",  # Use relative path to the FFmpeg binary in the repo
            "-i", video_file, 
            "-map", stream_index, 
            "-c:a", "libmp3lame", 
            "-q:a", "2", 
            output_filename
        ]
        
        print(f"Extracted {language} audio to {output_filename}")
        subprocess.run(command)
        print(os.listdir())
    return True



