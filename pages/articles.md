---
title: Articles
permalink: /articles/
---
<h1>All Articles</h1>
<ul class="post-list">
  {% assign posts_sorted = site.posts | sort: "date" | reverse %}
  {% for post in posts_sorted %}
    <li>
      <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
      <span class="muted"> · {{ post.date | date: "%b %d, %Y" }}</span>
    </li>
  {% endfor %}
</ul>
