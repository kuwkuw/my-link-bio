# My Link in Bio

## Project Overview
A personal link-in-bio page built with Flask where users can save links and view rich preview metadata (title, description, and image when available). The app now also includes a dedicated Contact page.

## Features
- Add links by submitting a name and URL from the home page (`/`).
- Auto-fetch Open Graph metadata for new/edited links using `requests` + BeautifulSoup.
- Edit existing links from `/edit/<link_index>`.
- Delete links from the home page.
- About page at `/about`.
- Contact page at `/contact` with a short message and an email link (`hello@example.com`).
- Custom error pages for 404 and 500 errors.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   python app.py
   ```
3. Open your browser at:
   - `http://127.0.0.1:5000/`

## Dependencies
- `Flask`: Web framework for routing, templates, and request handling.
- `requests`: Fetches remote page content for metadata extraction.
- `beautifulsoup4`: Parses HTML and extracts Open Graph tags.
- `gunicorn`: Production WSGI server (used for deployment environments).
