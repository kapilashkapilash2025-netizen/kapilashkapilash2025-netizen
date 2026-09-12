"""Render contribution cards using GitHub's API; standard library only."""
import datetime as dt
import json
import os
from pathlib import Path
import urllib.request

USER = 'kapilashkapilash2025-netizen'
QUERY = '''query { user(login: "kapilashkapilash2025-netizen") {
 contributionsCollection { contributionCalendar { totalContributions weeks {
 contributionDays { contributionCount date weekday }
 } } }
} }'''

def main():
    request = urllib.request.Request('https://api.github.com/graphql',
        data=json.dumps({'query': QUERY}).encode(),
        headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
                 'Content-Type': 'application/json', 'User-Agent': 'AXSON-PRIME-profile'})
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)
    if result.get('errors'):
        raise RuntimeError(result['errors'])
    calendar = result['data']['user']['contributionsCollection']['contributionCalendar']
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    days = [d for w in calendar['weeks'] for d in w['contributionDays'] if d['date'] <= today]
    if not days:
        raise RuntimeError('No contribution calendar returned')
    longest = run = 0
    for day in days:
        run = run + 1 if day['contributionCount'] else 0
        longest = max(longest, run)
    current = 0
    tail = days[:-1] if days[-1]['date'] == today and not days[-1]['contributionCount'] else days
    for day in reversed(tail):
        if not day['contributionCount']:
            break
        current += 1
    assets = Path(__file__).resolve().parents[1] / 'assets'
    def write(name, height, title, body):
        (assets / name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" viewBox="0 0 1000 {height}" role="img"><title>{title}</title><rect width="1000" height="{height}" rx="16" fill="#0b1727"/><g font-family="Arial, Helvetica, sans-serif">{body}</g></svg>\n')
    write('github-streak.svg', 190, 'GitHub contribution streak',
        f'<text x="36" y="38" fill="#67e8f9" font-size="17">CONTRIBUTION STREAK</text><text x="36" y="100" fill="#f0f9ff" font-size="40">{current} days</text><text x="36" y="129" fill="#a8c5d8" font-size="16">Current streak</text><text x="350" y="100" fill="#f0f9ff" font-size="40">{longest} days</text><text x="350" y="129" fill="#a8c5d8" font-size="16">Longest in returned year</text><text x="36" y="166" fill="#a8c5d8" font-size="13">GitHub contribution calendar · Updated {today} UTC · Today may still be in progress</text>')
    body = f'<text x="36" y="38" fill="#67e8f9" font-size="17">CONTRIBUTION ACTIVITY</text><text x="36" y="65" fill="#a8c5d8" font-size="15">{calendar["totalContributions"]} contributions in the returned year · Updated {today} UTC</text>'
    colors = ['#172c40', '#164e63', '#0e7490', '#0891b2', '#38bdf8']
    for x, week in enumerate(calendar['weeks']):
        for day in week['contributionDays']:
            if day['date'] > today:
                continue
            n = day['contributionCount']
            color = colors[0 if n == 0 else 1 if n < 3 else 2 if n < 6 else 3 if n < 10 else 4]
            body += f'<rect x="{36+x*17}" y="{86+day["weekday"]*17}" width="13" height="13" rx="3" fill="{color}"><title>{day["date"]}: {n} contributions</title></rect>'
    body += f'<text x="36" y="235" fill="#a8c5d8" font-size="13">{days[0]["date"]} — {days[-1]["date"]} · Includes contributions visible to the API</text>'
    write('github-activity.svg', 260, 'GitHub contribution activity', body)

if __name__ == '__main__':
    main()
