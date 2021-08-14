from typing import Optional as Opt

from .tables import Edium, orm


def create_edium(
    title: str,
    kind: Opt[str],
    url: Opt[str],
    comment: Opt[str]
) -> None:
    """Create an Edium."""
    kind = "" if kind is None else kind

    with orm.db_session:
        edium = Edium(title=title, kind=kind)
        if url is not None:
            edium.add_element("url", url)
        if comment is not None:
            edium.add_element("comment", comment)
