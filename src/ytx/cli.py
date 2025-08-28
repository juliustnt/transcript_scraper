import argparse
from .captions import fetch_transcript
from .io_utils import save_transcript

def main() -> None:
    ap = argparse.ArgumentParser(description="YouTube transcript fetcher (yt-dlp based)")
    ap.add_argument("url", help="YouTube URL or ID")
    ap.add_argument("mode", nargs="?", default="plain", choices=["plain", "srt"], help="Output format")
    ap.add_argument("--cookies", dest="cookie_path", help="Path to cookies.txt (Netscape format)")
    ap.add_argument(
        "--browser",
        dest="browser_cookie",
        choices=["edge", "chrome", "firefox", "brave", "vivaldi", "chromium"],
        help="Try cookies from this browser if needed",
    )
    ap.add_argument("--no-browser-cookies", action="store_true", help="Never attempt browser cookies")
    args = ap.parse_args()

    browser_opt = None if args.no_browser_cookies else args.browser_cookie

    video_id, transcript = fetch_transcript(
        args.url,
        output_format=args.mode,
        browser_cookie=browser_opt,
        cookie_path=args.cookie_path,
    )

    out_path = save_transcript(transcript, video_id, output_format=args.mode)
    print(f"[saved] {out_path}\n")

if __name__ == "__main__":
    main()
