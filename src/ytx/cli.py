import argparse
from .captions import fetch_transcript
from .io_utils import save_transcript

def main() -> None:
    argument_parser = argparse.ArgumentParser(description="YouTube transcript fetcher (yt-dlp based)")

    group = argument_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", "-u", help="YouTube URL or ID")
    group.add_argument("--input", "-i", help="Path to file with URLs/IDs (one per line)")

    # TODO: implementing --clean arg (NLP standardized dataset) and --corrections arg (JSON file with corrections)
    
    argument_parser.add_argument("mode", nargs="?", default="plain", choices=["plain", "srt"], help="Output format")
    argument_parser.add_argument("--cookies", dest="cookie_path", help="Path to cookies.txt (Netscape format)")
    argument_parser.add_argument(
        "--browser",
        dest="browser_cookie",
        choices=["edge", "chrome", "firefox", "brave", "vivaldi", "chromium"],
        help="Try cookies from this browser if needed",
    )
    argument_parser.add_argument("--no-browser-cookies", action="store_true", help="Never attempt browser cookies")
    args = argument_parser.parse_args()

    browser_opt = None if args.no_browser_cookies else args.browser_cookie
 
    if args.input:
        with open(args.input, "r", encoding="utf-8") as file:
            urls = [line.strip() for line in file if line.strip()]
        
        for url in urls:
            try:
                video_id, transcript = fetch_transcript(
                    url,
                    output_format=args.mode,
                    browser_cookie=browser_opt,
                    cookie_path=args.cookie_path,
                )
                out_path = save_transcript(transcript, video_id, output_format=args.mode)
                print(f"[saved] {out_path}\n")
            except Exception as e:
                print(f"[error] Failed to fetch transcript for {url}: {e}\n")
    elif args.url:
        video_id, transcript = fetch_transcript(
            args.url,
            output_format=args.mode,
            browser_cookie=browser_opt,
            cookie_path=args.cookie_path,
        )
        out_path = save_transcript(transcript, video_id, output_format=args.mode)
        print(f"[saved] {out_path}\n")
    else:
        argument_parser.print_help()

if __name__ == "__main__":
    main()
