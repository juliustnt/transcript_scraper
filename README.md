# YouTube Transcript Extractor (ytx)

A command-line tool to fetch and save YouTube video transcripts in plain text or SRT format, using `yt-dlp` and supporting cookies for private or age-restricted videos.

## Features
- Extracts transcripts from YouTube videos (supports both manual and auto-generated captions)
- Output formats: plain text (`.txt`) or SRT (`.srt`)
- Handles cookies from browser or file for restricted videos
- Saves output to the `output/` directory

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/juliustnt/transcript_scraper.git
   cd transcript_scraper
   ```
2. **Install dependencies:**
   ```sh
   pip install -e .
   ```
   This will install `yt-dlp` and `requests` as required dependencies.

## Usage

Run the CLI tool with:

```sh
ytx-transcript <YouTube URL or ID> [plain|srt] [--cookies <cookies.txt>] [--browser <browser>] [--no-browser-cookies]
```

### Arguments
- `<YouTube URL or ID>`: The video to fetch the transcript from
- `[plain|srt]`: Output format (default: `plain`)
- `--input <PATH>`: Path to a text file containing multiple YouTube URLs/IDs (one per line). Mutually exclusive with `<YouTube URL or ID>`
- `--cookies <cookies.txt>`: Path to a cookies.txt file (Netscape format)
- `--browser <browser>`: Try to use cookies from a browser (`edge`, `chrome`, `firefox`, `brave`, `vivaldi`, `chromium`)
- `--no-browser-cookies`: Never attempt to use browser cookies

### Example

Fetch a transcript in plain text:
```sh
ytx-transcript https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

Fetch a transcript in SRT format and save using Chrome cookies:
```sh
ytx-transcript https://www.youtube.com/watch?v=dQw4w9WgXcQ srt --browser chrome
```

## Output
- Transcripts are saved in the `output/` directory, named after the video ID and format (e.g., `dQw4w9WgXcQ.txt` or `dQw4w9WgXcQ.srt`).

## Project Structure
```
transcript_scraper/
├── pyproject.toml
├── README.md
├── output/
└── src/
    └── ytx/
        ├── __init__.py
        ├── captions.py
        ├── cli.py
        ├── io_utils.py
        └── parse.py
```
