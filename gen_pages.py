from pathlib import Path

import mkdocs_gen_files

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
    relative_path = path.relative_to(src_root)

    is_init = relative_path.name.startswith("__")
    is_root_init = is_init and len(relative_path.parts) <= 1
    if relative_path.name == "__pycache__" or is_root_init:
        continue

    if is_init:
        doc_path = Path("reference", relative_path.parent, "index.md")
    else:
        doc_path = Path("reference", relative_path).with_suffix(".md")

    with mkdocs_gen_files.open(doc_path, "w") as f:
        if is_init:
            ident = path.with_suffix("").parent.parts[1:]
        else:
            ident = path.with_suffix("").parts[1:]

        print(f"# `{ident[-1]}`", file=f)
        print("::: " + ".".join(ident), file=f)
        if is_init:
            print("\toptions:", file=f)
            print("\t\tshow_submodules: false", file=f)
