#!/usr/bin/env python3
import datetime
from pathlib import Path
from subprocess import check_output

import requests
from dateutil.parser import isoparse

DOMAIN = 'google.com'
TG_TOKEN = 'YOUR TOKEN HERE'
# TG_CHAT_ID = 879777248
TG_CHAT_ID = -1


def log_tg(msg: str):
    print(msg)
    requests.get(f"https://api.telegram.org/{TG_TOKEN}/sendMessage",
                 params={'chat_id': TG_CHAT_ID, 'text': msg, 'disable_web_page_preview': True})


def check(domain: str):
    date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    p = Path(f'data/domain-{domain}-whois.txt')
    p.parent.mkdir(parents=True, exist_ok=True)
    new = check_output(['whois', domain]).decode('utf-8')

    # Remove database update line
    lines = []
    db_update_date = 'Not found'
    for i, line in enumerate(new.split('\n')):
        if line.startswith('>>> Last update of Whois database:'):
            print(line)
            db_update_date = line.replace('>>> Last update of Whois database: ', '').replace(' <<<', '')
            db_update_date = isoparse(db_update_date).astimezone().strftime('%Y-%m-%d %H:%M')
        else:
            lines.append(line)

    new = '\n'.join(lines)

    def report(msg: str, out: bool):
        log_tg(f'Check on {date} (DB {db_update_date}): \n> {msg}')
        if out:
            log_tg('\n'.join(new.split('\n')[:20]))

    if p.is_file():
        old = p.read_text('utf-8')
        if old == new:
            report(f'No change detected.', False)
        else:
            report('Change detected.', True)
    else:
        report("The domain haven't been checked before.", True)

    p.write_text(new)


if __name__ == '__main__':
    check(DOMAIN)
