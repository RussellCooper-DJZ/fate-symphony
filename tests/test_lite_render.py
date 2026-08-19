import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "fate.py"


class LiteRenderTests(unittest.TestCase):
    def test_lite_profile_writes_a_bounded_wav(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "preview.wav"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--lite", "--preview-seconds", "2", "--output", str(output)],
                check=True,
                capture_output=True,
                text=True,
                timeout=60,
            )

            self.assertIn("Reverb: skipped", result.stdout)
            self.assertTrue(output.exists())
            with wave.open(str(output), "rb") as wav:
                self.assertEqual(wav.getframerate(), 11025)
                self.assertEqual(wav.getnchannels(), 1)
                self.assertEqual(wav.getsampwidth(), 2)
                self.assertLessEqual(wav.getnframes(), 2 * 11025)


if __name__ == "__main__":
    unittest.main()
