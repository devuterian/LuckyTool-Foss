#!/usr/bin/env bash
# Launch the real signed APK without bypassing activation or changing hook defaults.
set -euo pipefail
VERSION="${1:?Version required}"
PACKAGE='com.fosstool.app'
ACTIVITY='com.fosstool.app/.ui.activity.MainActivity'
mkdir -p smoke
adb install -r "dist/FossTool_${VERSION}.apk"
adb shell appops set "$PACKAGE" MANAGE_EXTERNAL_STORAGE allow
adb logcat -c

launch_and_dump() {
  local name="$1"
  adb shell am force-stop "$PACKAGE"
  adb shell am start -W -n "$ACTIVITY" > "smoke/${name}-launch.txt"
  sleep 4
  adb shell pidof "$PACKAGE" > "smoke/${name}-pid.txt"
  test -s "smoke/${name}-pid.txt"
  timeout 45 adb shell uiautomator dump /sdcard/foss-window.xml
  adb pull /sdcard/foss-window.xml "smoke/${name}.xml"
  adb exec-out screencap -p > "smoke/${name}.png"
  adb shell cmd locale get-app-locales "$PACKAGE" > "smoke/${name}-locale.txt"
}

launch_and_dump first-korean
python3 - <<'PY'
import pathlib, xml.etree.ElementTree as ET
p = pathlib.Path('smoke/first-korean.xml')
text = '\n'.join(x.attrib.get('text', '') for x in ET.parse(p).getroot().iter())
assert '모듈' in text, 'The Korean module activation dialog was not shown.'
assert '활성화' in text, 'The module activation warning was not localized.'
print('First launch: Korean module UI displayed without a crash.')
PY

# An explicit system app-language choice must survive process restarts.
adb shell cmd locale set-app-locales "$PACKAGE" --locales en
launch_and_dump selected-english
python3 - <<'PY'
import xml.etree.ElementTree as ET
text = '\n'.join(x.attrib.get('text', '') for x in ET.parse('smoke/selected-english.xml').getroot().iter())
assert '모듈' not in text, 'The selected English locale was overwritten.'
assert 'module' in text.lower() or 'xposed' in text.lower(), 'The module UI was not displayed.'
print('Selected language: English persisted after process restart.')
PY

adb shell cmd locale set-app-locales "$PACKAGE" --locales ko
launch_and_dump restored-korean
python3 - <<'PY'
import xml.etree.ElementTree as ET
text = '\n'.join(x.attrib.get('text', '') for x in ET.parse('smoke/restored-korean.xml').getroot().iter())
assert '모듈' in text and '활성화' in text, 'Switching back to Korean failed.'
print('Language switching: Korean restored successfully.')
PY
adb logcat -b crash -d > smoke/crash-log.txt
if grep -q 'Process: com.fosstool.app' smoke/crash-log.txt; then
  cat smoke/crash-log.txt
  echo 'The app crashed during the smoke test.'
  exit 1
fi
printf '%s\n' 'PASS: signed APK install; Korean first launch; English choice survives restart; Korean restoration; no app crash.' \
  'Scope: Android 15 AOSP emulator only. Real ColorOS/LSPosed hooks were not tested.' > smoke/RESULT.txt
