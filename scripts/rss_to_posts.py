#!/usr/bin/env python3
import datetime
import os
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

def extract_keywords(title):
    """Simple keyword extraction from title"""
    words = re.findall(r'\w+', title.lower())
    stopwords = {"the", "and", "of", "in", "to", "a", "for", "with", "on"}
    keywords = [w for w in words if w not in stopwords]
    return keywords[:10]  # limit to 10 keywords

# ----- Fetch videos -----
ydl_opts = {
    "extract_flat": True,  # Only metadata
    "skip_download": True,
    "quiet": True,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(channel_url, download=False)
    videos = info.get("entries", [])
    if not videos:
        videos = [info]

# ----- Generate posts -----
created = 0
for video in videos:
    if not video:
        continue

    title = video.get("title", "Untitled") or "Untitled"
    video_id = video.get("id", "")
    description = video.get("description", "") or ""
    thumbnail = video.get("thumbnail", "") or ""
    upload_date = video.get("upload_date", None)

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

    update_existing = True  # set to False if you don't want to update
    if md_path.exists() and not update_existing:
        continue

    # SEO-friendly content
    seo_intro = f"Learn about '{title}' from Lakbir Elomari's YouTube channel. This video covers key points and tutorials for better understanding."
    keywords = extract_keywords(title)

    # Front matter
    safe_title = title.replace('"', "'")
    fm = [
        "---",
        f'title: "{safe_title}"',
        f"date: {dt.strftime('%Y-%m-%d %H:%M:%S %z')}",
        f"youtube_id: {video_id}",
        f'image: "{thumbnail}"',
        f"tags: [{', '.join(keywords)}]",
        "---",
        ""
    ]

    # Body with YouTube embed
    body = textwrap.dedent(f"""
    {{% include youtube-privacy.html id="{video_id}" %}}
    """).strip()

    # Combine everything
    content = "\n".join(fm) + f"description: |\n  " + description.replace("\n", "\n  ") + "\n  " + seo_intro + "\n" + body + "\n"

    # Write to file
    with md_path.open("w", encoding="utf-8") as f:
        f.write(content)

    created += 1

print(f"Created {created} new post(s).")
