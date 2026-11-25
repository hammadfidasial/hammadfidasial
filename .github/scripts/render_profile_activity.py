"""Frame the generated contribution snake and add verified calendar totals."""

import json
import sys
from datetime import date
from html import escape
from pathlib import Path


def streak_length(counts):
    longest = current = 0
    for count in counts:
        current = current + 1 if count else 0
        longest = max(longest, current)
    return longest


def format_date(day):
    return date.fromisoformat(day).strftime("%d %b %Y").lstrip("0")


def render(calendar, snake, username):
    days = [day for week in calendar["weeks"] for day in week["contributionDays"]]
    counts = [day["contributionCount"] for day in days]
    peak = max(days, key=lambda day: day["contributionCount"])
    metrics = [
        ("CONTRIBUTIONS", f'{calendar["totalContributions"]:,}', "CONTRIBUTION CALENDAR"),
        ("ACTIVE DAYS", str(sum(count > 0 for count in counts)), f"ACROSS {len(days)} DAYS"),
        ("LONGEST STREAK", str(streak_length(counts)), "CONSECUTIVE DAYS"),
        ("BUSIEST DAY", str(peak["contributionCount"]),
         format_date(peak["date"]) if peak["contributionCount"] else "NO ACTIVITY"),
    ]
    handle = escape(username)
    start, end = format_date(days[0]["date"]), format_date(days[-1]["date"])
    groups = []
    for index, (label, value, detail) in enumerate(metrics):
        x = 57 + index * 283
        groups.append(f'''
    <g transform="translate({x} 70)">
      <g class="metric" style="--delay:{index * .11:.2f}s">
      <text class="mono" fill="#D792B1" font-size="13" letter-spacing="1.8">{label}</text>
      <text class="serif" y="48" fill="#FFF2F6" font-size="48">{value}</text>
      <text class="mono" y="72" fill="#CCB4C0" font-size="12">{detail}</text>
      </g>
    </g>''')
    stats = "".join(groups)
    labels = []
    last_month = days[0]["date"][:7]
    for index, week in enumerate(calendar["weeks"]):
        day = date.fromisoformat(week["contributionDays"][0]["date"])
        month = day.isoformat()[:7]
        if month != last_month and 2 < index < 52:
            x = 52 + (18 + 16 * index) * 1.25
            labels.append(f'<text x="{x:g}" y="184">{day:%b}</text>')
        last_month = month
    preview = snake.replace("<svg ", '<svg x="52" y="151" ', 1)
    preview = preview.replace('width="880" height="192"', 'width="1100" height="240"', 1)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 436" width="1200" height="436" role="img" aria-labelledby="title desc">
  <title id="title">GitHub contributions for @{handle}</title>
  <desc id="desc">Contribution calendar from {start} to {end}. {metrics[0][1]} contributions, {metrics[1][1]} active days, and a longest streak of {metrics[2][1]} days. The snake is refreshed daily.</desc>
  <defs>
    <linearGradient id="wine" x2="1" y2="1"><stop stop-color="#160C13"/><stop offset="1" stop-color="#321827"/></linearGradient>
    <radialGradient id="glow"><stop stop-color="#803855" stop-opacity=".62"/><stop offset="1" stop-color="#803855" stop-opacity="0"/></radialGradient>
  </defs>
  <style>
    .mono {{font-family:ui-monospace,Consolas,monospace}}
    .serif {{font-family:Georgia,"Times New Roman",serif}}
    @media (prefers-reduced-motion:no-preference) {{
      .metric {{animation:appear .7s ease both;animation-delay:var(--delay)}}
    }}
    @media (prefers-reduced-motion:reduce) {{
      rect.c, rect.u {{animation:none!important}}
      rect.s {{display:none}}
    }}
    @keyframes appear {{from{{opacity:0;transform:translateY(8px)}}}}
  </style>
  <rect x="1" y="1" width="1198" height="434" rx="19" fill="url(#wine)" stroke="#724358"/>
  <ellipse cx="898" cy="123" rx="296" ry="110" fill="url(#glow)" opacity=".75"/>
  <path d="M57 163h1087m-826-112v91m283-91v91m283-91v91" stroke="#724358" opacity=".65"/>
  {stats}
  <g class="mono" fill="#CCB4C0" font-size="12">{"".join(labels)}</g>
  {preview}
  <path d="M57 380h1087" stroke="#724358" opacity=".65"/>
  <text class="mono" x="57" y="409" font-size="13" fill="#CCB4C0">@{handle} · {start} to {end} · Refreshed daily</text>
  <text class="mono" x="1144" y="409" text-anchor="end" font-size="13" fill="#D792B1">GITHUB CONTRIBUTIONS</text>
</svg>
'''


def main():
    calendar_file, snake_file, output_file, username = sys.argv[1:]
    response = json.loads(Path(calendar_file).read_text())
    calendar = response["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    snake = Path(snake_file).read_text()
    Path(output_file).write_text(render(calendar, snake, username))


if __name__ == "__main__":
    main()
