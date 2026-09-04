from fix_lint import save_file_content


def test_save_file_content_normalizes_crlf(tmp_path):
    path = tmp_path / "page.md"

    save_file_content(path, "uma\r\nduas\r\n")

    assert path.read_bytes() == b"uma\nduas\n"
