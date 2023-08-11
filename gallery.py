"""Gallery."""

import random
from functools import lru_cache
from pathlib import Path

import flask
from PIL import Image

app = flask.Flask(__name__)


def get_random_prefix() -> str:
    """Get a randomly generated 5 character prefix."""
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=5))  # noqa: S311


@lru_cache
def get_gallery(gallery_path: Path) -> dict[str, list[dict[str, str]]]:
    """
    Get the images in the gallery, creating URLs, downscaling them, and returning a list of images.

    Parameters
    ----------
    gallery_path : Path
        Path to the gallery directory.

    Returns
    -------
    dict[str, list[dict[str, str]]]
        Dictionary with the date of the photo and a list of images.
    """
    gallery: dict[str, list[dict[str, str]]] = {}
    extensions = (".jpg", ".png")
    if not Path("./static/images").exists():
        Path("./static/images").mkdir(parents=True, exist_ok=True)

    if Path("./static/images").exists():
        for file in Path("./static/images").glob("*"):
            file.unlink()

    image_paths = [
        image_path
        for extension in extensions
        for image_path in gallery_path.glob(f"*{extension}")
    ]

    for image_path in image_paths:
        image = Image.open(image_path)
        prefix = get_random_prefix()
        image.thumbnail((300, 300), Image.Resampling.LANCZOS)
        image.save(f"./static/images/{prefix}-{image_path.name}", "JPEG")
        exif = image.getexif()
        date = exif[306].split()[0].replace(":", "-")
        image_url = flask.url_for(
            "static",
            filename=f"images/{prefix}-{image_path.name}",
        )
        image_data = {"url": image_url, "name": f"{prefix}-{image_path.name}"}
        if date in gallery:
            gallery[date].append(image_data)
        else:
            gallery[date] = [image_data]

    return gallery


@app.get("/")
def index() -> str:
    """Index."""
    if not Path("./images").exists():
        Path("./images").mkdir(parents=True, exist_ok=True)

    gallery = get_gallery(Path("./images"))
    gallery_sorted = sorted(gallery.items(), key=lambda x: x[0], reverse=True)

    return flask.render_template("index.html", gallery=gallery_sorted)
