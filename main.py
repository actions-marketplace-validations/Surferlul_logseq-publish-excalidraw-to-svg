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
            print("::debug::[found]", svg)
            yield draw, svg
        else:
            eprint("::error::[missing]", svg)
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
    home_md_file = None
    if len(argv) > 2:
        home_md_file = Path(argv[2]).expanduser()
        if not home_md_file:
            home_md_file = None
    pages, draws = get_draws(vault_path)

    missing_any_svgs = False

    replace_dict = {}
    for draw, svg in iter_svgs(vault_path, draws):
        if svg is None:
            replace_dict[f"[[{draw}]]"] = "<h1 style='color: #ff0000'>MISSING IMAGE</h1>"
            missing_any_svgs = True
        else:
            replace_dict[f"[[{draw}]]"] = f"![{draw}](../{svg})"

    for page in pages:
        with open(page) as f:
            content = f.read()

        for prev, new in replace_dict.items():
            content = content.replace(prev, new)

        with open(page, "w") as f:
            f.write(content)

    if missing_any_svgs and home_md_file is not None:
        with open(home_md_file, "a") as f:
            f.write("\n" + """
- <h1 style="color: red;">Some drawings were not loaded</h1>
\t- ## How to fix as a Contributor
\t\t- drawings are located in <vault path>/draws
\t\t- each ".excalidraw" drawing file should have an equivalent ".svg" file in <vault path>/assets/excalidraw_svg with the same basename
\t\t- ### Example
\t\t  ```
\t\t  <vault path>/draws/2023-10-08-21-23-31.excalidraw
\t\t  <vault path>/assets/excalidraw_svg/2023-10-08-21-23-31.svg
\t\t  ```
\t\t- to create a missing svg file, head to https://excalidraw.com/, paste the .excalidraw file, Click the Hamburger Menu > Export Image
\t\t\t- Enable "Background" and check if you need Dark or Light theme
\t\t\t- Click "SVG" and copy to <vault path>/assets/excalidraw_svgs
\t\t\t- Rename the file so the base names match
"""
                    )


if __name__ == "__main__":
    main()
