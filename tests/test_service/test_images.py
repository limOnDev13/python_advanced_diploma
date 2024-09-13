import pytest

from src.service.images import _file_extension


@pytest.mark.parametrize(
    "filename, result",
    (
        ("file.jpg", "jpg"),
        ("file.txt", "txt"),
        ("/file/file.txt", "txt"),
        ("~/file/file_file/file.txt", "txt"),
        ("file.file.file.txt", "txt"),
    ),
)
def test_file_extension(filename, result) -> None:
    """Testing func _file_extension on several filenames"""
    assert _file_extension(filename) == result


def test_file_extension_with_file_without_extension() -> None:
    """Testing func _file_extension with file without extension"""
    assert _file_extension("test") is None
