#!/usr/bin/env python3
"""
Pull and format reviews from Paper Trails.

Usage:
    python pull_reviews.py           # Uses profile from .env
    python pull_reviews.py login     # Save your login session
    python pull_reviews.py <id>      # Use specific profile
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from papertrails_scraper import PaperTrailsScraper, PaperReview, extract_profile_id


def format_review(review: PaperReview, no_markdown: bool = False) -> str:
    """Format a review for output."""
    lines = []

    if no_markdown:
        # Plain text format
        lines.append(f"[Review] {review.paper_title}")
        if review.paper_url:
            lines.append(review.paper_url)

        if review.rating is not None:
            stars = "★" * int(review.rating) + "☆" * (5 - int(review.rating))
            lines.append(f"{stars} ({review.rating}/5)")

        if review.review_text:
            lines.append("")
            lines.append(review.review_text)

        # Add cross-post link
        if review.paper_id:
            lines.append("")
            lines.append(f"https://www.papertrailshq.com/papers/{review.paper_id}#reviews")
    else:
        # Markdown format
        if review.paper_url:
            lines.append(f"## [{review.paper_title}]({review.paper_url})")
        else:
            lines.append(f"## {review.paper_title}")

        meta_parts = []
        if review.authors:
            author_str = ", ".join(review.authors[:3])
            if len(review.authors) > 3:
                author_str += " et al."
            meta_parts.append(author_str)
        if review.journal:
            meta_parts.append(f"*{review.journal}*")
        if meta_parts:
            lines.append(" ".join(meta_parts))

        if review.rating is not None:
            stars = "★" * int(review.rating) + "☆" * (5 - int(review.rating))
            lines.append(f"\n**Rating:** {stars} ({review.rating}/5)")

        if review.review_text:
            lines.append(f"\n{review.review_text}")

    return "\n".join(lines)


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Pull and format reviews from Paper Trails"
    )
    parser.add_argument(
        "profile",
        nargs="?",
        help="Profile ID/URL, or 'login'. Defaults to PAPERTRAILS_PROFILE env var",
    )
    parser.add_argument(
        "--raw", "-r",
        action="store_true",
        help="Output raw data instead of formatted text",
    )
    parser.add_argument(
        "--markdown", "-m",
        action="store_true",
        help="Output with markdown formatting",
    )

    args = parser.parse_args()

    # Handle login command
    if args.profile == "login":
        scraper = PaperTrailsScraper(headless=False)
        scraper.login_interactive()
        return

    # Get profile ID from args or env
    profile_id = args.profile or os.getenv("PAPERTRAILS_PROFILE")
    if not profile_id:
        print("Error: Provide a profile ID or set PAPERTRAILS_PROFILE in .env")
        sys.exit(1)

    profile_id = extract_profile_id(profile_id)
    print(f"Fetching reviews from profile: {profile_id}\n", file=sys.stderr)

    scraper = PaperTrailsScraper(headless=True)
    reviews = scraper.get_profile_reviews(profile_id)

    if not reviews:
        print("No reviews found.", file=sys.stderr)
        sys.exit(0)

    print(f"Found {len(reviews)} review(s)\n", file=sys.stderr)

    if args.raw:
        for review in reviews:
            print(f"TITLE: {review.paper_title}")
            print(f"AUTHORS: {', '.join(review.authors) if review.authors else 'N/A'}")
            print(f"YEAR: {review.year or 'N/A'}")
            print(f"RATING: {review.rating or 'N/A'}")
            print(f"REVIEW: {review.review_text or 'N/A'}")
            print(f"URL: {review.paper_url or 'N/A'}")
            print("-" * 40)
    else:
        for i, review in enumerate(reviews):
            if i > 0:
                print("\n" + "=" * 60 + "\n")
            print(format_review(review, no_markdown=not args.markdown))


if __name__ == "__main__":
    main()
