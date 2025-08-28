from pathlib import Path
from typing import Literal, Union
import json
import re
import tempfile

def sanitize_id(identifier: str) -> str:
    """Keep only alnum, dash, underscore for file identifiers."""
    return "".join(char for char in identifier if char.isalnum() or char in ("-", "_"))

def sanitize_filename(base_name: str, max_length: int = 180) -> str:
    """Sanitize a general filename while preserving common characters."""
    sanitized_name = re.sub(r"[^a-zA-Z0-9._ -]", "_", base_name).strip()
    return sanitized_name[:max_length] or "untitled"

def _sanitize_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)[:200]

def save_transcript(
    transcript: str,
    video_identifier: str,
    *,
    output_format: Literal["plain", "json", "srt"] = "plain",
    output_directory: Union[str, Path] = Path(__file__).resolve().parents[2] / "output",
) -> Path:
    """
    Save transcript and return the Path to the saved file.
    - Default output is ../../output (two levels above src/ytx).
    - Uses pathlib for robust path handling.
    - Writes atomically (temp file + rename).
    """
    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    base = _sanitize_filename(video_identifier)
    ext_map = {"plain": ".txt", "json": ".json", "srt": ".srt"}
    ext = ext_map[output_format]

    out_path = output_dir / f"{base}{ext}"

    if output_format == "json":
        content = json.dumps({"id": video_identifier, "transcript": transcript}, ensure_ascii=False, indent=2)
    else:
        content = transcript

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=output_dir, delete=False) as tf:
        tf.write(content)
        temp_name = Path(tf.name)
    temp_name.replace(out_path)

    return out_path