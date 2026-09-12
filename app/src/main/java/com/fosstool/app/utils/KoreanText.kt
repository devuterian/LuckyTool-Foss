package com.fosstool.app.utils

import java.util.Locale

object KoreanText {
    val isKorean: Boolean get() = Locale.getDefault().language == "ko"
    fun choose(korean: String, original: String): String = if (isKorean) korean else original
}
