from flask import Flask, redirect, render_template, request, url_for
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

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
    except requests.RequestException:
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
        links.append(
            {
                "name": site_name,
                "url": site_url,
                "title": open_graph_data["title"],
                "description": open_graph_data["description"],
                "image_url": open_graph_data["image_url"],
            }
        )

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


if __name__ == "__main__":
    app.run(debug=True)
