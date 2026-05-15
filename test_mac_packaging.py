import unittest
from pathlib import Path
from unittest.mock import patch

from formula_docx import OFFICE_MML2OMML_PATHS
from platform_utils import open_path


class MacPackagingTests(unittest.TestCase):
    def test_formula_converter_knows_common_macos_office_paths(self):
        paths = {str(path) for path in OFFICE_MML2OMML_PATHS}

        self.assertIn("/Applications/Microsoft Word.app/Contents/Resources/MML2OMML.XSL", paths)

    def test_open_path_uses_macos_open_command(self):
        with patch("sys.platform", "darwin"), patch("subprocess.Popen") as popen:
            open_path(Path("/tmp/example.docx"))

        popen.assert_called_once_with(["open", "/tmp/example.docx"])

    def test_mac_build_script_exists_and_builds_app(self):
        script = Path("build_mac.sh")

        self.assertTrue(script.exists())
        text = script.read_text(encoding="utf-8")
        self.assertIn("--windowed", text)
        self.assertIn("--name WordFormulaStudio", text)
        self.assertIn("assets/esdkaiyuan.icns", text)
        self.assertIn("create-dmg", text)
        self.assertIn("dist/WordFormulaStudio.app", text)


if __name__ == "__main__":
    unittest.main()
