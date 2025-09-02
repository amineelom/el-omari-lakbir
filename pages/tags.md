---
title: Tags
permalink: /tags/
---
<h1>Tags</h1>
{% assign tags = site.tags %}
<ul>
  {% for tag in tags %}
    <li id="{{ tag[0] }}"><strong>#{{ tag[0] }}</strong>
      <ul>
        {% for post in tag[1] %}
          <li><a href="{{ post.url | relative_url }}">{{ post.title }}</a> <span class="muted">({{ post.date | date: "%Y-%m-%d" }})</span></li>
        {% endfor %}
      </ul>
    </li>
  {% endfor %}
</ul>
