from __future__ import annotations
import requests
from urllib.parse import urlparse, parse_qs
from yt_dlp import YoutubeDL
from .parse import (
    convert_webvtt_to_srt,
    convert_srt_to_plain_text,
    _srv3_json_to_plain,
    _srv3_json_to_srt,
)

def get_video_id_from_url(url: str) -> str:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if host == "youtu.be":
        return parsed.path.lstrip("/")
    if "youtube" in host:
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [""])[0]
        if parsed.path.startswith("/shorts/"):
            parts = parsed.path.strip("/").split("/")
            if len(parts) >= 2:
                return parts[1]
    return url

class _SilentLogger:
    def debug(self, *_): ...
    def warning(self, *_): ...
    def error(self, *_): ...

def get_video_info(video_id: str, browser_cookie: str | None, cookie_path: str | None):
    options: dict = {
        "skip_download": True,
        "quiet": True,
        "logger": _SilentLogger(),
        "nocheckcertificate": True,
    }
    if cookie_path:
        options["cookiefile"] = cookie_path
    elif browser_cookie:
        options["cookiesfrombrowser"] = (browser_cookie, None, None, None)
    with YoutubeDL(options) as ydl:
        return ydl.extract_info(video_id, download=False)

def get_caption_url(video_data: dict, preferred_langs: tuple[str, ...] = ("en", "en-US", "en-GB")):
    def find(captions: dict | None):
        captions = captions or {}
        for lang in preferred_langs:
            if lang in captions and captions[lang]:
                caption = captions[lang][0]
                return caption["url"], (caption.get("ext") or caption.get("format_id") or "vtt")
        for _, items in captions.items():
            if items:
                caption = items[0]
                return caption["url"], (caption.get("ext") or caption.get("format_id") or "vtt")
        return None
    return find(video_data.get("subtitles")) or find(video_data.get("automatic_captions"))

def fetch_transcript(
    url: str,
    *,
    output_format: str = "plain",
    browser_cookie: str | None = None,
    cookie_path: str | None = None,
) -> tuple[str, str]:
    video_id = get_video_id_from_url(url)

    attempts: list[dict] = [{"browser_cookie": None, "cookie_path": None}]
    if cookie_path:
        attempts.append({"browser_cookie": None, "cookie_path": cookie_path})
    if browser_cookie:
        attempts.append({"browser_cookie": browser_cookie, "cookie_path": None})

    last_error: Exception | None = None
    for attempt in attempts:
        try:
            video_data = get_video_info(video_id, attempt["browser_cookie"], attempt["cookie_path"])
            caption = get_caption_url(video_data)
            if not caption:
                last_error = RuntimeError("No captions found.")
                continue

            caption_url, caption_format = caption
            response = requests.get(caption_url, timeout=30)
            response.raise_for_status()
            content = response.text
            preview = content.lstrip()[:20].upper()

            if preview.startswith("WEBVTT"):
                srt = convert_webvtt_to_srt(content)
                return video_id, (srt if output_format == "srt" else convert_srt_to_plain_text(srt))

            if content.lstrip().startswith("{") or content.lstrip().startswith("["):
                if output_format == "srt":
                    return video_id, _srv3_json_to_srt(content)
                return video_id, _srv3_json_to_plain(content)

            return video_id, content
        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"Failed to fetch captions. Last error: {last_error}")

get_transcript = fetch_transcript
