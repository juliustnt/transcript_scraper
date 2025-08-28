import json
import html

def convert_webvtt_to_srt(vtt_text: str) -> str:
    """
    Convert WebVTT to SRT format.
    """
    lines = [line.rstrip("\n") for line in vtt_text.splitlines()]
    srt_output, buffer, subtitle_index = [], [], 0

    def flush_buffer():
        nonlocal buffer, subtitle_index
        if not buffer:
            return
        converted_lines = []
        for line in buffer:
            if "-->" in line:
                line = line.replace(".", ",")
                if " --> " in line:
                    start, end = line.split(" --> ", 1)
                    end = end.split(" ", 1)[0]
                    line = f"{start} --> {end}"
            converted_lines.append(line)
        subtitle_index += 1
        srt_output.append(str(subtitle_index))
        srt_output.extend(converted_lines)
        srt_output.append("")
        buffer = []

    for line in lines:
        if line.strip().upper().startswith("WEBVTT"):
            continue
        if not line.strip():
            flush_buffer()
            continue
        buffer.append(line)
    flush_buffer()
    return "\n".join(srt_output).strip() + "\n"

def convert_srt_to_plain_text(srt_text: str, separator: str = "\n") -> str:
    """Strip indices/timestamps and join lines as readable text."""
    plain_text = []
    for block in srt_text.split("\n\n"):
        lines = block.strip().splitlines()
        if len(lines) >= 3 and "-->" in lines[1]:
            plain_text.append(" ".join(lines[2:]))
    return separator.join(plain_text)

def milliseconds_to_srt_time(milliseconds: int) -> str:
    hours = milliseconds // 3600000
    minutes = (milliseconds % 3600000) // 60000
    seconds = (milliseconds % 60000) // 1000
    millis = milliseconds % 1000
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

def _srv3_json_to_plain(json_text: str, drop_bracketed: bool = True, separator: str = "\n") -> str:
    """Convert YouTube SRV3 JSON to plain text."""
    data = json.loads(json_text)
    events = data.get("events", data if isinstance(data, list) else [])
    plain_text = []
    for event in events:
        segments = []
        for segment in event.get("segs", []):
            text = segment.get("utf8", "")
            if not text:
                continue
            text = text.replace("\n", " ")
            text = html.unescape(text)
            if drop_bracketed and text.strip().startswith("[") and text.strip().endswith("]"):
                continue
            if text.strip():
                segments.append(text)
        if segments:
            plain_text.append(" ".join(segments))
    return separator.join(plain_text)

def _srv3_json_to_srt(json_text: str, drop_bracketed: bool = True) -> str:
    """Convert YouTube SRV3 JSON to SRT format."""
    data = json.loads(json_text)
    events = data.get("events", data if isinstance(data, list) else [])
    srt_output = []
    subtitle_index = 1
    for event in events:
        segments = []
        for segment in event.get("segs", []):
            text = segment.get("utf8", "")
            if not text:
                continue
            text = text.replace("\n", " ")
            text = html.unescape(text)
            if drop_bracketed and text.strip().startswith("[") and text.strip().endswith("]"):
                continue
            if text.strip():
                segments.append(text)
        if not segments:
            continue
        start_time = int(event.get("tStartMs", 0))
        duration = int(event.get("dDurationMs", 0))
        end_time = start_time + duration
        srt_output.append(str(subtitle_index))
        srt_output.append(f"{milliseconds_to_srt_time(start_time)} --> {milliseconds_to_srt_time(end_time)}")
        srt_output.append(" ".join(segments))
        srt_output.append("")
        subtitle_index += 1
    return "\n".join(srt_output).strip() + ("\n" if srt_output else "")
