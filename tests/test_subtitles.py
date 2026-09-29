"""Regression checks for supplied-romaji inputs and display selection."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('subtitles', ROOT / 'skills/karaoke-pv/scripts/subtitles.py')
subtitles = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subtitles)


class SubtitleInputs(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'examples/timeline.json').read_text(encoding='utf-8'))

    def output(self, data, **kwargs):
        with tempfile.TemporaryDirectory() as folder:
            report = subtitles.export(data, folder, draft=True, **kwargs)
            return (Path(folder, 'romaji.srt').read_text(encoding='utf-8'),
                    Path(folder, 'romaji.ass').read_text(encoding='utf-8'), report)

    def test_missing_japanese_has_no_empty_caption_line(self):
        data = json.loads((ROOT / 'examples/romaji-only.json').read_text(encoding='utf-8'))
        srt, ass, _ = self.output(data)
        self.assertIn('00:00:01,250 --> 00:00:03,500\nAoi sora\n', srt)
        self.assertNotIn('Dialogue: 0,', ass)
        self.assertEqual(ass.count('Dialogue:'), 2)

    def test_romaji_display_hides_japanese_without_mutating_input(self):
        original = copy.deepcopy(self.data)
        srt, ass, report = self.output(self.data, display='romaji')
        self.assertNotIn('青い空', srt + ass)
        self.assertIn('Aoi sora', srt)
        self.assertEqual(report['display'], 'romaji')
        self.assertEqual(self.data, original)

    def test_bilingual_output_remains_supported(self):
        srt, ass, _ = self.output(self.data)
        self.assertIn('青い空\nAoi sora', srt)
        self.assertEqual(ass.count('Dialogue:'), 4)

    def test_cues_allow_empty_or_absent_japanese(self):
        self.data['cues'][0]['ja'] = ''
        del self.data['cues'][1]['ja']
        srt, ass, _ = self.output(self.data)
        self.assertIn('Aoi sora', srt)
        self.assertNotIn('Dialogue: 0,', ass)

    def test_optional_japanese_still_rejects_invalid_content(self):
        for invalid in (None, ' ', '{\\pos(0,0)}', 'a\nb'):
            with self.subTest(invalid=invalid):
                self.data['cues'][0]['ja'] = invalid
                with self.assertRaises(ValueError):
                    subtitles.validate(self.data, draft=True)

    def test_romaji_and_review_remain_required(self):
        with self.assertRaisesRegex(ValueError, 'unreviewed'):
            subtitles.validate(self.data)
        del self.data['cues'][0]['romaji']
        with self.assertRaisesRegex(ValueError, 'romaji'):
            subtitles.validate(self.data, draft=True)

    def test_timestamp_carry(self):
        self.assertEqual(subtitles.timestamp(59.9999), '00:01:00,000')
        self.assertEqual(subtitles.timestamp(59.9999, True), '0:01:00.00')


if __name__ == '__main__':
    unittest.main()
