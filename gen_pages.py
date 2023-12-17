from pathlib import Path

import mkdocs_gen_files
import regex

src_root = Path("src/downmixer")


def _create_pages_file(module_path: Path):
    with mkdocs_gen_files.open(module_path.joinpath(".pages"), "w") as f:
        print(f"title: {module_path.stem}", file=f)


def _iterate_subdirectories(dir_path: Path):
    _create_pages_file(Path("reference", dir_path.relative_to(src_root)))

    for directory in dir_path.iterdir():
        if directory.name.startswith("__") or directory.is_file():
            continue
        _iterate_subdirectories(directory)
        _create_pages_file(Path("reference", dir_path.relative_to(src_root)))


for path in src_root.glob("*"):
    if path.is_file() or path.name.startswith("__"):
        continue

    _iterate_subdirectories(path)

for path in src_root.glob("**/*.py"):
    if regex.search(r"__.*__.py", path.name) is not None:
        continue

    relative_path = path.relative_to(src_root)
    doc_path = Path("reference", relative_path).with_suffix(".md")

    with mkdocs_gen_files.open(doc_path, "w") as f:
        ident = ".".join(path.with_suffix("").parts[1:])
        print(f"# `{path.stem}`", file=f)
        print("::: " + ident, file=f)
