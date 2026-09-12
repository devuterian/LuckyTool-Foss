package com.fosstool.app.utils

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
