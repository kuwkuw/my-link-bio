from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

# In-memory storage for links. This resets when the app restarts.
links = [
    {"name": "GitHub", "url": "https://github.com"},
    {"name": "LinkedIn", "url": "https://www.linkedin.com"},
    {"name": "YouTube", "url": "https://www.youtube.com"},
]


@app.route("/")
def home():
    return render_template("index.html", page_title="My Links", links=links)


@app.route("/add", methods=["POST"])
def add_link():
    site_name = request.form.get("site_name", "").strip()
    site_url = request.form.get("site_url", "").strip()

    if site_name and site_url:
        links.append({"name": site_name, "url": site_url})

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
            links[link_index] = {"name": site_name, "url": site_url}
            return redirect(url_for("home"))

    return render_template("edit.html", page_title="Edit Link", link=links[link_index], link_index=link_index)


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
