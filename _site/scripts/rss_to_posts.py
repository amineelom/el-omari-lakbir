#!/usr/bin/env python3
import datetime
import os
import pathlib
import re
import sys
import textwrap
from urllib.parse import parse_qs, urlparse

import feedparser


# Utils
def slugify(value):
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    return value[:80] or "video"

def get_channel_config():
    cfg_path = pathlib.Path("_config.yml")
    if not cfg_path.exists():
        print("ERROR: _config.yml not found", file=sys.stderr)
        sys.exit(1)
    feed_url = None
    with cfg_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("yt_feed_url:"):
                feed_url = line.split(":", 1)[1].strip().strip('"').strip("'")
                break
    if not feed_url or "youtube.com/feeds/videos.xml" not in feed_url:
        print("ERROR: Set yt_feed_url in _config.yml", file=sys.stderr)
        sys.exit(1)
    return feed_url

def youtube_id_from_link(link):
    if "watch" in link:
        q = parse_qs(urlparse(link).query)
        return q.get("v", [""])[0]
    m = re.search(r'/videos/([^/?]+)', link)
    if m:
        return m.group(1)
    return ""

def main():
    feed_url = get_channel_config()
    feed = feedparser.parse(feed_url)

    posts_dir = pathlib.Path("_posts")
    posts_dir.mkdir(parents=True, exist_ok=True)

    created = 0
    for entry in feed.entries:
        # Safe string conversion
        title = str(entry.get("title", "Untitled")).strip()
        description = str(entry.get("summary", "")).strip()
        published_parsed = entry.get("published_parsed") or entry.get("updated_parsed")

        if published_parsed:
            dt = datetime.datetime(*published_parsed[:6])
        else:
            dt = datetime.datetime.utcnow()

        # youtube id
        yt_id = entry.get("yt_videoid") or entry.get("yt_video_id") or youtube_id_from_link(str(entry.get("link", "")))

        # thumbnail
        thumb = ""
        if "media_thumbnail" in entry and entry.media_thumbnail:
            thumb = str(entry.media_thumbnail[0].get("url", ""))
        elif "media_group" in entry and hasattr(entry.media_group, "thumbnail"):
            thumb = str(getattr(entry.media_group, "thumbnail", {}).get("url", ""))

        # build filename
        date_str = dt.strftime("%Y-%m-%d")
        slug = slugify(title)
        md_path = posts_dir / f"{date_str}-{slug}.md"

        if md_path.exists():
            continue

        safe_title = title.replace('"', "'")

        fm = [
            "---",
            f'title: "{safe_title}"',
            f"date: {dt.strftime('%Y-%m-%d %H:%M:%S %z')}",
            f"youtube_id: {yt_id}",
            f'image: "{thumb}"',
            "description: |",
            "  " + description.replace("\n", "\n  "),
            "---",
            ""
        ]

        body = f'{{% include youtube-privacy.html id="{yt_id}" %}}'

        content = "\n".join(fm) + "\n" + body + "\n"

        with md_path.open("w", encoding="utf-8") as f:
            f.write(content)

        created += 1

    print(f"Created {created} new post(s).")

if __name__ == "__main__":
    main()
