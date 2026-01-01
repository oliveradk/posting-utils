# Paper Trails Review Puller

Pull and format paper reviews from Paper Trails.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
playwright install chromium
```

Add your profile ID to `.env`:
```
PAPERTRAILS_PROFILE=your_profile_id_here
```

## Usage

```bash
source .venv/bin/activate

# Pull and format reviews (uses .env profile)
python pull_reviews.py

# Plain text output (no markdown)
python pull_reviews.py --no-markdown

# Save to file
python pull_reviews.py > reviews.md

# Use specific profile
python pull_reviews.py <profile_id>
```

## Options

- `--no-markdown`, `-n`: Plain text output without markdown formatting
- `--raw`, `-r`: Output raw data fields
