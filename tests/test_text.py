from speakeasy.text import clean_for_speech


class TestCleanForSpeech:
    """Tests for the clean_for_speech function."""

    def test_removes_fenced_code_blocks(self):
        text = "Here is code:\n```python\nprint('hello')\n```\nDone."
        result = clean_for_speech(text)
        assert "print" not in result
        assert "Done." in result

    def test_keeps_inline_code_content(self):
        text = "Use the `say` command to speak."
        result = clean_for_speech(text)
        assert "say" in result
        assert "`" not in result

    def test_removes_markdown_headers(self):
        text = "# Title\n## Subtitle\nSome content."
        result = clean_for_speech(text)
        assert result.startswith("Title")
        assert "Subtitle" in result
        assert "#" not in result

    def test_removes_bold_and_italic(self):
        text = "This is **bold** and *italic* text."
        result = clean_for_speech(text)
        assert "bold" in result
        assert "italic" in result
        assert "*" not in result

    def test_removes_underscored_emphasis(self):
        text = "This is __bold__ and _italic_ text."
        result = clean_for_speech(text)
        assert "bold" in result
        assert "italic" in result
        assert "_" not in result

    def test_strips_markdown_links_keeps_text(self):
        text = "Check [this link](https://example.com) for info."
        result = clean_for_speech(text)
        assert "this link" in result
        assert "https" not in result
        assert "[" not in result

    def test_removes_bare_urls(self):
        text = "Visit https://example.com/foo for details."
        result = clean_for_speech(text)
        assert "https" not in result
        assert "Visit" in result

    def test_removes_bullet_markers(self):
        text = "Items:\n- First\n- Second\n* Third"
        result = clean_for_speech(text)
        assert "First" in result
        assert "Second" in result
        assert "Third" in result
        assert "- " not in result
        assert "* " not in result

    def test_removes_numbered_list_markers(self):
        text = "Steps:\n1. First\n2. Second"
        result = clean_for_speech(text)
        assert "First" in result
        assert "Second" in result

    def test_collapses_multiple_newlines(self):
        text = "Paragraph one.\n\n\n\n\nParagraph two."
        result = clean_for_speech(text)
        assert "\n\n\n" not in result

    def test_strips_whitespace(self):
        text = "  \n  Hello world.  \n  "
        result = clean_for_speech(text)
        assert result == "Hello world."

    def test_empty_input(self):
        assert clean_for_speech("") == ""

    def test_plain_text_unchanged(self):
        text = "This is a normal sentence with no markdown."
        result = clean_for_speech(text)
        assert result == text
