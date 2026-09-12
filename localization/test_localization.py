#!/usr/bin/env python3
"""Offline regression checks for the Korean localization."""
from collections import Counter
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET
import generate

ROOT = Path(__file__).resolve().parent.parent
RES = ROOT / 'app/src/main/res'


def strings(folder):
    result = {}
    for path in (RES / folder).glob('*.xml'):
        for entry in ET.parse(path).getroot():
            if entry.tag == 'string':
                key = entry.attrib['name']
                if key in result:
                    raise AssertionError(f'Duplicate string {key} in {folder}')
                result[key] = entry
    return result


class KoreanLocalizationTests(unittest.TestCase):
    def test_generated_files_match_source(self):
        files, count = generate.outputs()
        self.assertEqual(count, 1038)
        for path, content in files.items():
            self.assertEqual(path.read_bytes(), content, str(path))

    def test_runtime_strings_have_complete_korean_coverage(self):
        base = ET.parse(RES / 'values/runtime_strings.xml').getroot()
        ko = ET.parse(RES / 'values-ko/runtime_strings.xml').getroot()
        self.assertEqual({x.attrib['name'] for x in base}, {x.attrib['name'] for x in ko})
        self.assertEqual(len(base), 24)

    def test_all_format_arguments_preserved(self):
        base, ko = strings('values'), strings('values-ko')
        for key, entry in ko.items():
            self.assertIn(key, base)
            self.assertEqual(Counter(generate.FORMAT.findall(base[key].text or '')),
                             Counter(generate.FORMAT.findall(entry.text or '')), key)

    def test_no_untranslated_chinese_in_korean_strings(self):
        for key, entry in strings('values-ko').items():
            self.assertFalse(re.search(r'[\u4e00-\u9fff]', entry.text or ''), key)
            self.assertTrue((entry.text or '').strip(), key)

    def test_all_user_facing_source_strings_are_covered(self):
        base, ko = strings('values'), strings('values-ko')
        self.assertEqual(set(base) - set(ko), generate.SKIP)
        for key in ko:
            self.assertNotEqual(base[key].get('translatable'), 'false', key)

    def test_resource_references_resolve(self):
        available = set(strings('values'))
        for path in (RES / 'values-ko').glob('*.xml'):
            for text in ET.parse(path).getroot().itertext():
                for key in re.findall(r'@string/([A-Za-z0-9_]+)', text):
                    self.assertIn(key, available, str(path))

    def test_language_selector_is_declared(self):
        ns = '{http://schemas.android.com/apk/res/android}'
        config = ET.parse(RES / 'xml/locale_config.xml').getroot()
        names = [x.attrib[ns + 'name'] for x in config]
        self.assertEqual(names[0], 'ko')
        self.assertEqual(len(names), len(set(names)))
        manifest = ET.parse(ROOT / 'app/src/main/AndroidManifest.xml').getroot()
        app = manifest.find('application')
        self.assertEqual(app.get(ns + 'localeConfig'), '@xml/locale_config')
        services = [x for x in app.findall('service')
                    if x.get(ns + 'name') == 'androidx.appcompat.app.AppLocalesMetadataHolderService']
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0].get(ns + 'exported'), 'false')

    def test_all_resource_xml_is_well_formed(self):
        for path in RES.rglob('*.xml'):
            ET.parse(path)


if __name__ == '__main__':
    unittest.main(verbosity=2)
