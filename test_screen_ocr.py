import types
from unittest.mock import patch, MagicMock
import pytest

import screen_ocr


# ── setup_tesseract ──────────────────────────────────────────────


class TestSetupTesseract:
    @patch("screen_ocr.shutil.which", return_value="/usr/bin/tesseract")
    def test_returns_true_when_on_path(self, mock_which):
        assert screen_ocr.setup_tesseract() is True

    @patch("screen_ocr.os.path.isfile", return_value=True)
    @patch("screen_ocr.shutil.which", return_value=None)
    def test_returns_true_when_windows_default_exists(self, mock_which, mock_isfile):
        assert screen_ocr.setup_tesseract() is True
        mock_isfile.assert_called_once_with(
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )

    @patch("screen_ocr.os.path.isfile", return_value=False)
    @patch("screen_ocr.shutil.which", return_value=None)
    def test_returns_false_when_not_found(self, mock_which, mock_isfile):
        assert screen_ocr.setup_tesseract() is False


# ── extract_text ─────────────────────────────────────────────────


class TestExtractText:
    @patch("screen_ocr.pytesseract.image_to_string", return_value="hello world\n")
    @patch("screen_ocr.ImageGrab.grab")
    def test_returns_stripped_ocr_text(self, mock_grab, mock_ocr):
        mock_grab.return_value = MagicMock()
        result = screen_ocr.extract_text((0, 0, 100, 100))
        mock_grab.assert_called_once_with(bbox=(0, 0, 100, 100))
        mock_ocr.assert_called_once_with(mock_grab.return_value)
        assert result == "hello world"

    @patch("screen_ocr.pytesseract.image_to_string", return_value="  \n")
    @patch("screen_ocr.ImageGrab.grab")
    def test_returns_empty_string_when_no_text(self, mock_grab, mock_ocr):
        mock_grab.return_value = MagicMock()
        result = screen_ocr.extract_text((0, 0, 50, 50))
        assert result == ""


# ── RegionSelector event handlers ────────────────────────────────


class TestRegionSelectorEvents:
    """Test the coordinate logic in event handlers without a real tkinter window."""

    def _make_selector(self):
        """Create a RegionSelector with a mocked tkinter root."""
        with patch("screen_ocr.tk.Tk") as MockTk:
            mock_root = MagicMock()
            MockTk.return_value = mock_root
            mock_canvas = MagicMock()
            with patch("screen_ocr.tk.Canvas", return_value=mock_canvas):
                sel = screen_ocr.RegionSelector()
        return sel

    def test_on_press_records_start_coords(self):
        sel = self._make_selector()
        event = types.SimpleNamespace(x=10, y=20, x_root=110, y_root=220)
        sel.on_press(event)
        assert sel.start_x == 110
        assert sel.start_y == 220

    def test_on_release_sets_bbox_for_valid_region(self):
        sel = self._make_selector()
        sel.start_x = 100
        sel.start_y = 200
        event = types.SimpleNamespace(x_root=250, y_root=400)
        sel.on_release(event)
        assert sel.bbox == (100, 200, 250, 400)

    def test_on_release_normalises_reversed_drag(self):
        sel = self._make_selector()
        sel.start_x = 300
        sel.start_y = 400
        event = types.SimpleNamespace(x_root=100, y_root=200)
        sel.on_release(event)
        assert sel.bbox == (100, 200, 300, 400)

    def test_on_release_ignores_tiny_selection(self):
        sel = self._make_selector()
        sel.start_x = 100
        sel.start_y = 200
        event = types.SimpleNamespace(x_root=103, y_root=202)
        sel.on_release(event)
        assert sel.bbox is None


# ── main ─────────────────────────────────────────────────────────


class TestMain:
    @patch("screen_ocr.setup_dpi_awareness")
    @patch("screen_ocr.setup_tesseract", return_value=False)
    def test_exits_when_tesseract_missing(self, mock_tess, mock_dpi):
        with pytest.raises(SystemExit) as exc_info:
            screen_ocr.main()
        assert exc_info.value.code == 1

    @patch("screen_ocr.extract_text", return_value="some text")
    @patch("screen_ocr.RegionSelector")
    @patch("screen_ocr.setup_tesseract", return_value=True)
    @patch("screen_ocr.setup_dpi_awareness")
    def test_prints_extracted_text(self, mock_dpi, mock_tess, MockSelector, mock_extract, capsys):
        MockSelector.return_value.run.return_value = (10, 20, 300, 400)
        screen_ocr.main()
        output = capsys.readouterr().out
        assert "some text" in output

    @patch("screen_ocr.RegionSelector")
    @patch("screen_ocr.setup_tesseract", return_value=True)
    @patch("screen_ocr.setup_dpi_awareness")
    def test_exits_when_no_region_selected(self, mock_dpi, mock_tess, MockSelector):
        MockSelector.return_value.run.return_value = None
        with pytest.raises(SystemExit) as exc_info:
            screen_ocr.main()
        assert exc_info.value.code == 0

    @patch("screen_ocr.extract_text", return_value="")
    @patch("screen_ocr.RegionSelector")
    @patch("screen_ocr.setup_tesseract", return_value=True)
    @patch("screen_ocr.setup_dpi_awareness")
    def test_prints_no_text_message(self, mock_dpi, mock_tess, MockSelector, mock_extract, capsys):
        MockSelector.return_value.run.return_value = (10, 20, 300, 400)
        screen_ocr.main()
        output = capsys.readouterr().out
        assert "No text detected" in output
