import re


def create_slug(title):
    slug = title.lower().replace(" ", "-")
    slug = re.sub(r"[^\w-]", "", slug)
    return slug
