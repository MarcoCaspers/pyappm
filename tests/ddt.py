import sys

sys.path.append("/proj/python/pyappm/src/pyappm")

from simple_toml import TomlReader, TomlWriter  # type: ignore
from pathlib import Path


# The test case
def test_toml():
    path = Path("tests/test.toml")
    with TomlReader(path) as reader:
        data = reader.read()
        assert data.tools.option == "value"

    with TomlWriter(path) as writer:
        data.tools.tool1.option = "value"
        data.tools.tool2.option = "value"
        writer.write(data)

    with TomlReader(path) as reader:
        data = reader.read()
        assert data.tools.tool1.option == "value"
        assert data.tools.tool2.option == "value"


def test_demo_toml():
    path = Path("tests/demo/pyapp.toml")
    with TomlReader(path) as reader:
        data = reader.read()
    print(data)
    with TomlWriter(path) as writer:
        writer.write(data)


print("Running test_toml")
test_toml()
print("Running test_demo_toml")
test_demo_toml()

print("Done")
