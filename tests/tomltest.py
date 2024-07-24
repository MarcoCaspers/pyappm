import sys
from pathlib import Path

sys.path.append("/proj/python/pyapp/src/")

from pyapp.simple_toml import TomlReader, TomlWriter, DotDict  # type: ignore


def test_toml_reader():
    print("Running TomlReader test")
    path = Path("tests/test.toml")
    with TomlReader(path) as reader:
        data = reader.read()
        assert data.tools.option == "value"
        print("Test passed")


def test_toml_writer():
    print("Running TomlWriter test")
    path = Path("tests/test.toml")
    if path.exists():
        path.unlink()
    data = DotDict({"tools": DotDict({"option": "value"})})
    with TomlWriter(path) as writer:
        writer.write(data)
    if not path.exists():
        print("Test failed")
        return
    print("Test passed")


def test_demo():
    print("Running demo test")
    path = Path("tests/demo/pyapp.toml")
    if path.exists():
        with TomlReader(path) as reader:
            data = reader.read()
            print(data.project.authors[0].name)
        print("Test passed")
    else:
        print("Test failed, file not found")


def create_test_toml():
    path = Path("tests/test.toml")
    if path.exists():
        path.unlink()
    data = DotDict({"tools": DotDict({"option": "value"})})
    data.project.authors = [DotDict({"name": "John Doe", "email": "j.doe@example.com"})]
    data.project.pythonrequired = ">=3.8"
    with TomlWriter(path) as writer:
        writer.write(data)
    with TomlReader(path) as reader:
        data = reader.read()
        print("data.tools.option:             ", data.tools.option)
        print("data.project.authors[0].name:  ", data.project.authors[0].name)
        print("data.project.authors[0].email: ", data.project.authors[0].email)
        print("data.project.pythonrequired:   ", data.project.pythonrequired)
        print("Test passed")


def test_pyapp_toml():
    path = Path("tests/demo/pyapp.toml")
    print("testing pyapp.toml")
    if path.exists():
        with TomlReader(path) as reader:
            data = reader.read()
            print("tools: ", data.tools)
            print("tools.env_create_tool: ", data.tools.env_create_tool)
        print("Test passed")
    else:
        print("Test failed, file not found")


def main() -> None:
    # test_toml_writer()
    # test_toml_reader()
    # test_demo()
    # create_test_toml()
    test_pyapp_toml()


if __name__ == "__main__":
    main()
