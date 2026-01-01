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
python pull_reviews.py > reviews.txt
```

## Options

- `--markdown`, `-m`: Output with markdown formatting
- `--raw`, `-r`: Output raw data fields
