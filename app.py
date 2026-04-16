import logging
import os

from flask import Flask, flash, redirect, render_template, request, url_for
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

# In-memory storage for links. This resets when the app restarts.
links = [
    {
        "name": "GitHub",
        "url": "https://github.com",
        "title": "not available",
        "description": "not available",
        "image_url": "not available",
    },
    {
        "name": "LinkedIn",
        "url": "https://www.linkedin.com",
        "title": "not available",
        "description": "not available",
        "image_url": "not available",
    },
    {
        "name": "YouTube",
        "url": "https://www.youtube.com",
        "title": "not available",
        "description": "not available",
        "image_url": "not available",
    },
]


def extract_open_graph_data(site_url):
    """Fetch metadata from a URL and return Open Graph title/description/image values."""
    default_value = "not available"
    open_graph_data = {
        "title": default_value,
        "description": default_value,
        "image_url": default_value,
    }

    try:
        # Use a browser-like user agent because some sites reject unknown clients.
        response = requests.get(
            site_url,
            timeout=8,
            headers={"User-Agent": "Mozilla/5.0 (compatible; LinkBioBot/1.0)"},
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logging.warning(
            "FetchLinkMetadata request failed: url=%s error=%s",
            site_url,
            str(e),
        )
        return open_graph_data

    soup = BeautifulSoup(response.text, "html.parser")

    og_title = soup.find("meta", property="og:title")
    og_description = soup.find("meta", property="og:description")
    og_image = soup.find("meta", property="og:image")

    if og_title and og_title.get("content"):
        open_graph_data["title"] = og_title["content"].strip() or default_value
    if og_description and og_description.get("content"):
        open_graph_data["description"] = og_description["content"].strip() or default_value
    if og_image and og_image.get("content"):
        open_graph_data["image_url"] = og_image["content"].strip() or default_value

    return open_graph_data


@app.route("/")
def home():
    return render_template("index.html", page_title="My Links", links=links)


@app.route("/add", methods=["POST"])
def add_link():
    site_name = request.form.get("site_name", "").strip()
    site_url = request.form.get("site_url", "").strip()

    if site_name and site_url:
        open_graph_data = extract_open_graph_data(site_url)
        default_value = "not available"
        if (
            open_graph_data.get("title") == default_value
            and open_graph_data.get("description") == default_value
            and open_graph_data.get("image_url") == default_value
        ):
            logging.warning("Metadata could not be retrieved for url=%s", site_url)
            flash(
                "we saved your link, but could not retrieve a preview for that URL.",
                "warning",
            )
        links.append(
            {
                "name": site_name,
                "url": site_url,
                "title": open_graph_data["title"],
                "description": open_graph_data["description"],
                "image_url": open_graph_data["image_url"],
            }
        )
        logging.info("Added new link: name=%s url=%s", site_name, site_url)

    return redirect(url_for("home"))


@app.route("/delete/<int:link_index>", methods=["POST"])
def delete_link(link_index):
    # Guard against invalid list indexes submitted in the URL.
    if 0 <= link_index < len(links):
        links.pop(link_index)

    return redirect(url_for("home"))


@app.route("/edit/<int:link_index>", methods=["GET", "POST"])
def edit_link(link_index):
    if not 0 <= link_index < len(links):
        return redirect(url_for("home"))

    if request.method == "POST":
        site_name = request.form.get("site_name", "").strip()
        site_url = request.form.get("site_url", "").strip()

        if site_name and site_url:
            open_graph_data = extract_open_graph_data(site_url)
            links[link_index] = {
                "name": site_name,
                "url": site_url,
                "title": open_graph_data["title"],
                "description": open_graph_data["description"],
                "image_url": open_graph_data["image_url"],
            }
            return redirect(url_for("home"))

    return render_template("edit.html", page_title="Edit Link", link=links[link_index], link_index=link_index)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html", page_title="Contact")


@app.errorhandler(404)
def page_not_found(error):
    # Flask docs recommend returning the template with the explicit status code.
    return render_template("404.html", page_title="Page Not Found"), 404


@app.errorhandler(500)
def internal_server_error(error):
    # Flask docs recommend returning the template with the explicit status code.
    return render_template("500.html", page_title="Internal Server Error"), 500


if __name__ == "__main__":
    app.run(debug=True)
