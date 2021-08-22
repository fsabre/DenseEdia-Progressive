"""Define some helper functions that are used in many files."""

import datetime
from typing import Optional as Opt


def get_url_title(url: str) -> Opt[str]:
    """Return a fitting title for the URL. None if not found."""
    from youtube_dl import DownloadError, YoutubeDL
    try:
        opts = {"quiet": True, "simulate": True}
        with YoutubeDL(opts) as ydl:
            video_info = ydl.extract_info(url)
            return video_info.get("title", None)
    except DownloadError:
        return None


def now() -> datetime.datetime:
    """Return the naive current time, without milliseconds."""
    return datetime.datetime.now().replace(microsecond=0)
