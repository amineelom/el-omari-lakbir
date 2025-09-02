#!/usr/bin/env python3
import datetime
import pathlib
import re
import textwrap

import yt_dlp

# ----- Configuration -----
channel_url = "https://www.youtube.com/@lakbirelomari"

posts_dir = pathlib.Path("_posts")
posts_dir.mkdir(parents=True, exist_ok=True)

# ----- Utils -----
def slugify(value):
    value = re.sub(r'[^\w\s-]', '', value or '').strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    return value[:80] or "video"

# ----- Fetch videos -----
ydl_opts_flat = {
    "extract_flat": False,
    "skip_download": True,
    "quiet": True,
}

with yt_dlp.YoutubeDL(ydl_opts_flat) as ydl:
    info = ydl.extract_info(channel_url, download=False)
    videos = info.get("entries", [])
    if not videos:
        videos = [info]

# ----- Generate posts -----
created = 0
ydl_opts_full = {
    "quiet": True,
}

with yt_dlp.YoutubeDL(ydl_opts_full) as ydl:
    for video in videos:
        if not video:
            continue

        # Fetch full metadata for each video
        video_info = ydl.extract_info(video["url"], download=False) if "url" in video else video

        title = video_info.get("title", "Untitled") or "Untitled"
        video_id = video_info.get("id", "")
        description = video_info.get("description", "") or ""
        thumbnail = video.get("thumbnail", "") or ""
        upload_date = video_info.get("upload_date", None)

        if upload_date:
            try:
                dt = datetime.datetime.strptime(upload_date, "%Y%m%d")
            except:
                dt = datetime.datetime.utcnow()
        else:
            dt = datetime.datetime.utcnow()

        slug = slugify(title)
        date_str = dt.strftime("%Y-%m-%d")
        md_path = posts_dir / f"{date_str}-{slug}.md"

        safe_title = title.replace('"', "'")

        fm = [
            "---",
            f'title: "{safe_title}"',
            f"date: {dt.strftime('%Y-%m-%d %H:%M:%S %z')}",
            f"youtube_id: {video_id}",
            f"thumbnail: \"{thumbnail}\"",   # <-- change from image: to thumbnail:
            "---",
            ""
        ]


        body = textwrap.dedent(f"""
        {{% include youtube-privacy.html id="{video_id}" %}}
        """).strip()

        content = "\n".join(fm) + f"description: |\n  " + description.replace("\n", "\n  ") + "\n" + body + "\n"

        with md_path.open("w", encoding="utf-8") as f:
            f.write(content)

        created += 1

print(f"Created {created} new post(s).")
