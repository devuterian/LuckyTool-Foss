#!/usr/bin/env python3
"""One-time, anchor-checked source migration for the Korean edition."""
from pathlib import Path
import re
import xml.etree.ElementTree as E
ROOT = Path(__file__).resolve().parent.parent
JAVA = ROOT / 'app/src/main/java/com/fosstool/app'
RES = ROOT / 'app/src/main/res'
if (JAVA / 'utils/LanguageSettings.kt').exists():
    raise SystemExit('Runtime migration is already integrated; no changes made.')

def patch(rel, old, new, count=None):
    p = ROOT / rel
    s = p.read_text()
    if old not in s:
        raise RuntimeError(f'Missing patch anchor: {rel}: {old[:100]}')
    if count is not None and s.count(old) != count:
        raise RuntimeError(f'Count mismatch: {rel}')
    p.write_text(s.replace(old, new))

def java_patch(path, old, new, count=None):
    patch('app/src/main/java/com/fosstool/app/' + path, old, new, count)

def add_import(path, imp):
    p = JAVA / path
    s = p.read_text()
    if f'import {imp}\n' not in s:
        s = re.sub(r'(package [^\n]+\n)', r'\1\nimport ' + imp + '\n', s, count=1)
        p.write_text(s)

EXTRA = {
    'battery_level_label': ('Battery level', '배터리 잔량'),
    'battery_status_label': ('Status', '상태'),
    'battery_health_label': ('Health', '배터리 상태'),
    'battery_chemistry_label': ('Technology', '배터리 종류'),
    'battery_health_good': ('Good', '정상'),
    'battery_health_overheat': ('Overheating', '과열'),
    'battery_health_dead': ('Failed', '손상됨'),
    'battery_health_overvoltage': ('Overvoltage', '과전압'),
    'battery_health_failure': ('Unspecified failure', '원인 불명의 이상'),
    'battery_health_cold': ('Too cold', '온도가 너무 낮음'),
    'battery_plug_ac': ('AC charger', '전원 어댑터'),
    'battery_plug_wireless': ('Wireless charger', '무선 충전'),
    'battery_unplugged': ('Not connected', '연결되지 않음'),
    'battery_info_row': ('%1$s: %2$s', '%1$s: %2$s'),
    'restore_key_error': ('Could not restore this setting: %1$s', '이 설정을 복원하지 못했어요: %1$s'),
    'preference_load_error': ('Could not load setting %1$d: %2$s', '설정 %1$d번을 불러오지 못했어요: %2$s'),
    'package_name_required': ('Select an app or enter its package name first.', '앱을 선택하거나 패키지 이름을 먼저 입력해 주세요.'),
    'activities_not_found': ('No activity information is available for this app.', '이 앱의 액티비티 정보를 찾지 못했어요.'),
    'browser_version_error': ('This browser version is not supported. Please check the installed version.', '지원하지 않는 브라우저 버전이에요. 설치된 버전을 확인해 주세요.'),
    'refresh_rate_apply_error': ('Could not apply the refresh rate setting: %1$s', '주사율 설정을 적용하지 못했어요: %1$s'),
    'shortcuts_update_error': ('Could not update app shortcuts.', '앱 바로가기를 설정하지 못했어요.'),
    'default_notification_channel': ('General notifications', '일반 알림'),
    'demo_notification_text': ('Notification preview', '알림 미리보기'),
    'clock_lunar_examples': ('N → lunar day\\nNN → lunar month and day\\nNNN → zodiac, month and day\\nNNNN → sexagenary year, zodiac, month and day\\nFF → period of day\\nGG → traditional two-hour period', 'N → 1일\\nNN → 2월 1일\\nNNN → 토끼띠 2월 1일\\nNNNN → 계묘년 토끼띠 2월 1일\\nFF → 새벽/오전/정오/오후/저녁/밤\\nGG → 자시/축시/인시/묘시'),
}
for suffix, idx in [('values', 0), ('values-ko', 1)]:
    root = E.Element('resources')
    for key, pair in EXTRA.items():
        E.SubElement(root, 'string', {'name': key}).text = pair[idx].replace("'", "\\'")
    E.indent(root, space='    ')
    p = RES / suffix / 'runtime_strings.xml'
    p.parent.mkdir(exist_ok=True)
    p.write_bytes(E.tostring(root, encoding='utf-8', xml_declaration=True) + b'\n')

p = JAVA / 'ui/fragment/BatteryInfoFragment.kt'
s = p.read_text()
start = s.index('        val sb = StringBuilder()')
end = s.index('\n    }', start)
s = s[:start] + '''        val unknown = getString(R.string.battery_status_unknown)
        val statusText = getString(when (status) {
            BatteryManager.BATTERY_STATUS_CHARGING -> R.string.battery_status_charging
            BatteryManager.BATTERY_STATUS_DISCHARGING -> R.string.battery_status_discharging
            BatteryManager.BATTERY_STATUS_FULL -> R.string.battery_status_full
            BatteryManager.BATTERY_STATUS_NOT_CHARGING -> R.string.battery_status_not_charging
            else -> R.string.battery_status_unknown
        })
        val healthText = getString(when (health) {
            BatteryManager.BATTERY_HEALTH_GOOD -> R.string.battery_health_good
            BatteryManager.BATTERY_HEALTH_OVERHEAT -> R.string.battery_health_overheat
            BatteryManager.BATTERY_HEALTH_DEAD -> R.string.battery_health_dead
            BatteryManager.BATTERY_HEALTH_OVER_VOLTAGE -> R.string.battery_health_overvoltage
            BatteryManager.BATTERY_HEALTH_UNSPECIFIED_FAILURE -> R.string.battery_health_failure
            BatteryManager.BATTERY_HEALTH_COLD -> R.string.battery_health_cold
            else -> R.string.battery_status_unknown
        })
        val plugText = when (plugged) {
            BatteryManager.BATTERY_PLUGGED_AC -> getString(R.string.battery_plug_ac)
            BatteryManager.BATTERY_PLUGGED_USB -> "USB"
            BatteryManager.BATTERY_PLUGGED_WIRELESS -> getString(R.string.battery_plug_wireless)
            0 -> getString(R.string.battery_unplugged)
            else -> unknown
        }
        fun row(label: Int, value: String) = getString(R.string.battery_info_row, getString(label), value)
        batteryInfoText.text = listOf(
            row(R.string.battery_level_label, if (batteryPct >= 0) "$batteryPct%" else unknown),
            row(R.string.battery_voltage, if (voltMV >= 0) "$voltMV mV" else unknown),
            row(R.string.battery_temperature, if (temperature >= 0) "$tempC °C" else unknown),
            row(R.string.battery_status_label, statusText),
            row(R.string.battery_health_label, healthText),
            row(R.string.battery_chemistry_label, technology?.takeIf { it.isNotBlank() } ?: unknown),
            row(R.string.battery_charger_type, plugText)
        ).joinToString("\\n")''' + s[end:]
p.write_text(s)

replacements = [
    ('ui/fragment/SettingsFragment.kt', 'context.toast("Error: $key")', 'context.toast(context.getString(R.string.restore_key_error, key))'),
    ('ui/fragment/XposedFragment.kt', 'context.toast("Error: $index ${preference.key}")', 'context.toast(context.getString(R.string.preference_load_error, index, preference.key.orEmpty()))'),
    ('ui/fragment/MemcConfigFragment.kt', 'ctx.toast("PackageName is null!")', 'ctx.toast(ctx.getString(R.string.package_name_required))'),
    ('ui/fragment/MemcConfigFragment.kt', 'context.toast("App data is null!")', 'context.toast(context.getString(R.string.activities_not_found))'),
    ('ui/fragment/SystemScope.kt', 'ctx.toast("Error: Please check your browser version!")', 'ctx.toast(ctx.getString(R.string.browser_version_error))'),
    ('utils/FuncUtils.kt', 'context.toast("apply $name Hz failed!")', 'context.toast(context.getString(R.string.refresh_rate_apply_error, name))'),
    ('utils/ShortcutUtils.kt', 'context.toast("Set Dynamic Shortcuts Error!")', 'context.toast(context.getString(R.string.shortcuts_update_error))'),
    ('utils/NotifyUtils.kt', 'const val DEFAULT_NOTICE_NAME = "默认通知"', 'fun defaultNoticeName(context: Context): String = context.getString(R.string.default_notification_channel)'),
    ('utils/NotifyUtils.kt', '.setContentTitle("标题")', '.setContentTitle(context.getString(R.string.app_name))'),
    ('utils/NotifyUtils.kt', '.setContentText("内容")', '.setContentText(context.getString(R.string.demo_notification_text))'),
]
for rel, old, new in replacements:
    java_patch(rel, old, new)
    add_import(rel, 'com.fosstool.app.R')
java_patch('ui/fragment/SystemScope.kt', '"None"', 'ctx.getString(R.string.cur_type_none)')
java_patch('ui/fragment/SystemScope.kt', 'formatDate("d/dd/d号/dd号")', 'formatDate(if (ctx.resources.configuration.locales[0].language == "ko") "d/dd/d일/dd일" else "d/dd/d号/dd号")')
p = JAVA / 'ui/fragment/SystemScope.kt'
s, n = re.subn(r'                            N -> 初一\n.*?                            GG -> 子时/丑时/寅时/卯时', r'                            ${ctx.getString(R.string.clock_lunar_examples)}', p.read_text(), flags=re.S)
assert n == 1
p.write_text(s)
for name in ['dialog_app_selector.xml', 'fragment_hide_intent_applist_layout.xml']:
    patch('app/src/main/res/layout/' + name, 'android:hint="Name / PackageName"', 'android:hint="@string/hide_app_intent_search_hint"')

(JAVA / 'utils/LanguageSettings.kt').write_text('''package com.fosstool.app.utils

import android.app.LocaleManager
import android.content.Context
import android.os.Build
import android.os.LocaleList
import androidx.appcompat.app.AppCompatDelegate
import androidx.core.os.LocaleListCompat
import androidx.preference.DropDownPreference
import com.fosstool.app.R

object LanguageSettings {
    fun initialize(context: Context) {
        val prefs = context.getSharedPreferences("app_language", Context.MODE_PRIVATE)
        if (prefs.getBoolean("initialized", false)) return
        if (Build.VERSION.SDK_INT >= 33) {
            val manager = context.getSystemService(LocaleManager::class.java)
            if (manager.applicationLocales.isEmpty) {
                manager.applicationLocales = LocaleList.forLanguageTags("ko")
            }
        } else {
            AppCompatDelegate.setApplicationLocales(LocaleListCompat.forLanguageTags("ko"))
        }
        prefs.edit().putBoolean("initialized", true).apply()
    }

    fun preference(context: Context) = DropDownPreference(context).apply {
        key = "app_language"
        title = context.getString(R.string.language)
        isPersistent = false
        isIconSpaceReserved = false
        entries = arrayOf(context.getString(R.string.follow_system), "한국어", "English",
            "简体中文", "繁體中文（台灣）", "繁體中文（香港）", "日本語", "Русский",
            "Українська", "Polski", "Čeština", "Română", "Tiếng Việt")
        entryValues = arrayOf("", "ko", "en", "zh-CN", "zh-TW", "zh-HK", "ja-JP", "ru-RU",
            "uk-UA", "pl-PL", "cs-CZ", "ro-RO", "vi-VN")
        value = AppCompatDelegate.getApplicationLocales().toLanguageTags()
        summaryProvider = androidx.preference.ListPreference.SimpleSummaryProvider.getInstance()
        setOnPreferenceChangeListener { _, selected ->
            AppCompatDelegate.setApplicationLocales(LocaleListCompat.forLanguageTags(selected as String))
            true
        }
    }
}
''')
add_import('ui/application/MyApplication.kt', 'com.fosstool.app.utils.LanguageSettings')
java_patch('ui/application/MyApplication.kt', '        super.onCreate()', '        super.onCreate()\n        LanguageSettings.initialize(this)', 1)
add_import('ui/fragment/SettingsFragment.kt', 'com.fosstool.app.utils.LanguageSettings')
java_patch('ui/fragment/SettingsFragment.kt', '            addPreference(DropDownPreference(context).apply {', '            addPreference(LanguageSettings.preference(context))\n            addPreference(DropDownPreference(context).apply {', 1)
patch('app/src/main/AndroidManifest.xml', '            android:allowBackup="true"', '            android:allowBackup="true"\n            android:localeConfig="@xml/locale_config"', 1)
patch('app/src/main/AndroidManifest.xml', '    </application>', '''        <service
                android:name="androidx.appcompat.app.AppLocalesMetadataHolderService"
                android:enabled="false"
                android:exported="false">
            <meta-data android:name="autoStoreLocales" android:value="true" />
        </service>
    </application>''', 1)
locales = ['ko', 'en', 'zh-CN', 'zh-TW', 'zh-HK', 'ja-JP', 'ru-RU', 'uk-UA', 'pl-PL', 'cs-CZ', 'ro-RO', 'vi-VN']
(RES / 'xml/locale_config.xml').write_text('<?xml version="1.0" encoding="utf-8"?>\n<locale-config xmlns:android="http://schemas.android.com/apk/res/android">\n' + ''.join(f'    <locale android:name="{lang}" />\n' for lang in locales) + '</locale-config>\n')

(JAVA / 'utils/KoreanText.kt').write_text('''package com.fosstool.app.utils

import java.util.Locale

object KoreanText {
    val isKorean: Boolean get() = Locale.getDefault().language == "ko"
    fun choose(korean: String, original: String): String = if (isKorean) korean else original
}
''')
clock = 'hook/statusbar/StatusBarClock.kt'
add_import(clock, 'com.fosstool.app.utils.KoreanText')
p = JAVA / clock
s = p.read_text()
start = s.index('        if (finalFormat.contains("NNNN"))')
end = s.index('        if (finalFormat.contains("dddd"))', start)
s = s[:start] + '''        // Translated dates have variable lengths; never slice by Chinese character offsets.
        finalFormat = Regex("NNNN|NNN|NN|N").replace(finalFormat) { token ->
            val style = when (token.value.length) { 1 -> 1; 2 -> 2; 3 -> 3; else -> 0 }
            val lunar = LunarHelperUtils(appClassLoader).generateLunarDate(style)
            "'" + lunar.replace("'", "''") + "'"
        }
''' + s[end:]
s = s.replace('"dddd", "dd号"', '"dddd", KoreanText.choose("dd일", "dd号")').replace('"ddd", "d号"', '"ddd", KoreanText.choose("d일", "d号")')
words = {'凌晨': '새벽', '上午': '오전', '中午': '정오', '下午': '오후', '傍晚': '저녁', '晚上': '밤', '子时': '자시', '丑时': '축시', '寅时': '인시', '卯时': '묘시', '辰时': '진시', '巳时': '사시', '午时': '오시', '未时': '미시', '申时': '신시', '酉时': '유시', '戌时': '술시', '亥时': '해시'}
for zh, ko in words.items():
    s = s.replace('"' + zh + '"', 'KoreanText.choose("' + ko + '", "' + zh + '")')
s = s.replace('        if (isZh(context)) {', '''        if (context.resources.configuration.locales[0].language == "ko") {
            val parts = mutableListOf<String>()
            if (isYear) parts.add("yyyy년")
            if (isMonth) parts.add("M월")
            if (isDay) parts.add("d일")
            if (isWeek) parts.add("E")
            dateFormat = parts.joinToString(if (isHideSpace) "" else " ")
            if (parts.isNotEmpty() && !isHideSpace && !isDoubleRow) dateFormat += " "
        } else if (isZh(context)) {''', 1)
p.write_text(s)
p = JAVA / 'hook/utils/sysui/LunarHelperUtils.kt'
s = p.read_text()
needle = '        chinese[1] = month\n'
addition = '''
        if (Locale.getDefault().language == "ko") {
            val stems = arrayOf("갑", "을", "병", "정", "무", "기", "경", "신", "임", "계")
            val branches = arrayOf("자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해")
            val animals = arrayOf("쥐", "소", "호랑이", "토끼", "용", "뱀", "말", "양", "원숭이", "닭", "개", "돼지")
            val yearIndex = chinese[0] - 1864
            val yearText = stems[Math.floorMod(yearIndex, 10)] + branches[Math.floorMod(yearIndex, 12)] + "년"
            val zodiacText = animals[Math.floorMod(chinese[0] - 4, 12)] + "띠"
            val isLeap = leapMonth in 1..12 && month - 12 == leapMonth
            val monthText = (if (isLeap) "윤" else "") + (if (month > 12) month - 12 else month) + "월"
            val dayText = "${chinese[2]}일"
            return@runCatching when (style) {
                1 -> dayText
                2 -> "$monthText $dayText"
                3 -> "$zodiacText $monthText $dayText"
                else -> "$yearText $zodiacText $monthText $dayText"
            }
        }
'''
assert s.count(needle) == 1
p.write_text(s.replace(needle, needle + addition))
java_patch('hook/utils/sysui/LunarHelperUtils.kt', 'SimpleDateFormat(pattern, Locale.getDefault())', 'SimpleDateFormat(pattern, Locale.ROOT)', 1)
p = ROOT / 'gradle.properties'
p.write_text(re.sub(r'^systemProp\..*[Pp]roxy.*\n?', '', p.read_text(), flags=re.M))
(ROOT / 'app/version.properties').write_text('versionCode=20004\n')
patch('app/build.gradle.kts', 'compileSdk = 36', 'compileSdk = 37', 1)
print('Runtime localization source migration completed.')
