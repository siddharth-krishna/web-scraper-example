## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Cron job to run scraper periodically

```bash
crontab -e
```

Add the following line to run the script every 30 minutes:
```
*/30 * * * * /path/to/web-scraper-example/run.sh >> /path/to/web-scraper-example/out.log 2>&1
```

## TODO
- Incognito mode
- Why doesn't headless firefox driver work in Ubuntu?