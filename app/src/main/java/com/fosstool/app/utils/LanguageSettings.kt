package com.fosstool.app.utils

import android.app.LocaleManager
import android.content.Context
import android.os.Build
import android.os.LocaleList
import androidx.appcompat.app.AppCompatDelegate
import androidx.core.os.LocaleListCompat
import androidx.preference.DropDownPreference
import com.fosstool.app.R

/** App locales have one persistence owner per Android version. */
object LanguageSettings {
    private const val PREFS = "app_language"
    private const val INITIALIZED = "initialized"
    private const val LANGUAGE_TAG = "language_tag"

    fun initialize(context: Context) {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        if (Build.VERSION.SDK_INT >= 33) {
            // The framework owns persistence on Android 13+. AppCompat auto-storage
            // is disabled to avoid its first-Activity migration replacing this
            // initial locale with an empty, never-created legacy locale file.
            if (!prefs.getBoolean(INITIALIZED, false)) {
                val manager = context.getSystemService(LocaleManager::class.java)
                if (manager.applicationLocales.isEmpty) {
                    manager.applicationLocales = LocaleList.forLanguageTags("ko")
                }
                prefs.edit().putBoolean(INITIALIZED, true).apply()
            }
        } else {
            // Before Android 13, restore our own preference on every process start.
            // An empty tag deliberately means "follow system", not "uninitialized".
            val tag = prefs.getString(LANGUAGE_TAG, "ko").orEmpty()
            AppCompatDelegate.setApplicationLocales(LocaleListCompat.forLanguageTags(tag))
            if (!prefs.contains(LANGUAGE_TAG)) {
                prefs.edit().putString(LANGUAGE_TAG, tag).apply()
            }
        }
    }

    private fun currentTags(context: Context): String =
        if (Build.VERSION.SDK_INT >= 33) {
            context.getSystemService(LocaleManager::class.java).applicationLocales.toLanguageTags()
        } else {
            AppCompatDelegate.getApplicationLocales().toLanguageTags()
        }

    private fun select(context: Context, tags: String) {
        if (Build.VERSION.SDK_INT >= 33) {
            context.getSystemService(LocaleManager::class.java).applicationLocales =
                LocaleList.forLanguageTags(tags)
        } else {
            context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
                .edit().putString(LANGUAGE_TAG, tags).apply()
            AppCompatDelegate.setApplicationLocales(LocaleListCompat.forLanguageTags(tags))
        }
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
        value = currentTags(context)
        summaryProvider = androidx.preference.ListPreference.SimpleSummaryProvider.getInstance()
        setOnPreferenceChangeListener { _, selected ->
            select(context, selected as String)
            true
        }
    }
}
