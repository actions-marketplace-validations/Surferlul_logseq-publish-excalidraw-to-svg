from pathlib import Path
from sys import argv, stderr
import re

excalidraw_re = re.compile(r"\[\[(.*\.excalidraw)\]\]")


def eprint(*args, **kwargs):
    print(*args, file=stderr, **kwargs)


def iter_svgs(vault_path, draws):
    for draw in draws:
        svg = Path("assets/excalidraw_svg").joinpath(Path(draw).with_suffix(".svg").name)
        if vault_path.joinpath(svg).is_file():
            print("[found]", svg)
            yield draw, svg
        else:
            eprint("[missing]:", svg)
            yield draw, None


def iter_refs(vault_path):
    pages = [path for path in vault_path.joinpath("pages").glob("*") if path.is_file()]
    for page in pages:
        with open(page) as f:
            content = f.read()
        for ref_match in excalidraw_re.finditer(content):
            yield page, ref_match


def get_draws(vault_path):
    draws = set()
    pages = set()
    for page, ref_match in iter_refs(vault_path):
        draws.add(ref_match[1])
        pages.add(page)
    return pages, draws


def main() -> None:
    """
    Replaces excalidraw file references with svg references
    If <drawing_name>.svg exists in assets/excalidraw_svg it will be used,
    otherwise it will be replaced with

    :return:
    """
    vault_path = Path(argv[1]).expanduser()
    pages, draws = get_draws(vault_path)

    replace_dict = {}
    for draw, svg in iter_svgs(vault_path, draws):
        if svg is None:
            replace_dict[f"[[{draw}]]"] = "<h1 style='color: #ff0000'>MISSING IMAGE</h1>"
        else:
            replace_dict[f"[[{draw}]]"] = f"![]({svg})"

    for page in pages:
        with open(page) as f:
            content = f.read()

        for prev, new in replace_dict.items():
            content = content.replace(prev, new)

        with open(page, "w") as f:
            f.write(content)


if __name__ == "__main__":
    main()
