import atexit
import shutil
import subprocess
from pathlib import Path

__all__ = [
    "RtspToHls",
]

DIR_PATH = Path(__file__).parent

for sub_dir in DIR_PATH.iterdir():
    if sub_dir.is_dir() and sub_dir.name != "__pycache__":
        shutil.rmtree(sub_dir)

class RtspToHls:
    data = {}
    
    @staticmethod
    def add(rtsp_url: str): # return path of output file
        if rtsp_url:
            _hash = str(hash(rtsp_url))
            path: Path = DIR_PATH / _hash
            
            if RtspToHls.data.get(rtsp_url, None):
                RtspToHls.data[rtsp_url]["ref_count"] += 1
            else:
                path.mkdir()
                with open(DIR_PATH / "stdout.txt", "a") as out_file, open(DIR_PATH / "stderr.txt", "a") as err_file:
                    process = subprocess.Popen(
                        [
                            "ffmpeg",
                            "-i", rtsp_url,
                            "-c:v", "libx264",
                            "-f", "hls",
                            "-r", "10",
                            "-hls_time", "5",
                            "-hls_flags", "delete_segments",
                            "-hls_segment_filename", path / "segment_%03d.ts",
                            path / "output.m3u8",
                        ],
                        stdout=out_file,
                        stderr=err_file,
                    )
                RtspToHls.data[rtsp_url] = {
                    "ref_count": 1,
                    "subprocess": process,
                }

            return path / "output.m3u8"
    
    @staticmethod
    def clear():
        rtsp_urls = [key for key in RtspToHls.data.keys()]
        for rtsp_url in rtsp_urls:
            while RtspToHls.data.get(rtsp_url, None):
                RtspToHls.sub(rtsp_url)
    
    @staticmethod
    def sub(rtsp_url: str):
        if rtsp_url:
            _hash = str(hash(rtsp_url))
            path: Path = DIR_PATH / _hash
            
            if RtspToHls.data.get(rtsp_url, None):
                RtspToHls.data[rtsp_url]["ref_count"] -= 1
                if RtspToHls.data[rtsp_url]["ref_count"] == 0:
                    RtspToHls.data[rtsp_url]["subprocess"].kill()
                    shutil.rmtree(path)
                    del RtspToHls.data[rtsp_url]

atexit.register(RtspToHls.clear)
