import com.github.megatronking.stringfog.plugin.StringFogExtension
import java.util.Properties

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android") version "2.4.0"
    id("org.jetbrains.kotlin.plugin.serialization") version "2.4.0"
    id("com.google.devtools.ksp") version "2.3.10"
    id("stringfog")
}

// Private signing is optional for local builds. Release CI signs the unsigned
// APK with an isolated key; debug builds always use Android's debug keystore.
val keystoreProperties = Properties().apply {
    val props = rootProject.file("keystore/keystore.properties")
    if (props.isFile) props.inputStream().use { load(it) }
}
val appVersionCode = 20004
val appVersionName = "2.0.3-ko.1"

android {
    if (keystoreProperties.containsKey("storeFile")) {
        signingConfigs {
            create("release") {
                enableV1Signing = true
                enableV2Signing = true
                enableV3Signing = true
                storeFile = file(keystoreProperties.getProperty("storeFile"))
                keyAlias = keystoreProperties.getProperty("keyAlias")
                keyPassword = keystoreProperties.getProperty("keyPassword")
                storePassword = keystoreProperties.getProperty("storePassword")
            }
        }
    }
    compileSdk { version = release(37) { minorApiLevel = 0 } }
    namespace = "com.fosstool.app"
    defaultConfig {
        applicationId = "com.fosstool.app"
        minSdk = 30
        targetSdk = 36
        versionCode = appVersionCode
        versionName = appVersionName
        buildConfigField("String", "APP_CENTER_SECRET", "\"${getAppCenterSecret()}\"")
    }
    buildTypes {
        release {
            isDebuggable = false
            isMinifyEnabled = false
            isShrinkResources = false
            signingConfig = signingConfigs.findByName("release")
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
        debug {
            isDebuggable = true
            isMinifyEnabled = false
            isShrinkResources = false
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlin { jvmToolchain(17) }
    buildFeatures {
        aidl = true
        viewBinding = true
        buildConfig = true
    }
    applicationVariants.all {
        val variantBuildType = buildType.name
        outputs.all {
            @Suppress("DEPRECATION")
            if (this is com.android.build.gradle.api.ApkVariantOutput) {
                outputFileName = "FossTool_${appVersionName}_${variantBuildType}.apk"
            }
        }
    }
    androidResources.additionalParameters.addAll(
        arrayOf("--allow-reserved-package-id", "--package-id", "0x64")
    )
}

configurations.all {
    resolutionStrategy {
        force("org.jetbrains.kotlin:kotlin-stdlib:2.4.0")
        force("org.jetbrains.kotlin:kotlin-stdlib-jdk7:2.4.0")
        force("org.jetbrains.kotlin:kotlin-stdlib-jdk8:2.4.0")
        force("org.jetbrains.kotlin:kotlin-reflect:2.4.0")
    }
}

dependencies {
    compileOnly("de.robv.android.xposed:api:82")
    implementation("com.highcapable.yukihookapi:api:1.3.2")
    ksp("com.highcapable.yukihookapi:ksp-xposed:1.3.2")
    implementation("org.luckypray:dexkit:2.2.0")
    implementation("com.google.android.material:material:1.12.0")
    implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.8.4")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("androidx.preference:preference-ktx:1.2.1")
    implementation("androidx.swiperefreshlayout:swiperefreshlayout:1.1.0")
    implementation("androidx.navigation:navigation-fragment-ktx:2.7.7")
    implementation("androidx.navigation:navigation-ui-ktx:2.7.7")
    implementation("com.github.getActivity:XXPermissions:18.2")
    implementation("com.github.simplepeng.SpiderMan:spiderman:v1.2.3")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")
    implementation("com.squareup.okhttp3:okhttp:4.11.0")
    implementation("com.github.liangjingkanji:Net:3.6.2")
    implementation("com.github.topjohnwu.libsu:core:5.0.5")
    implementation("com.github.topjohnwu.libsu:service:5.0.5")
    implementation("com.microsoft.appcenter:appcenter-analytics:5.0.2")
    implementation("com.microsoft.appcenter:appcenter-crashes:5.0.2")
    compileOnly("com.github.megatronking.stringfog:xor:5.0.0")
}

configure<StringFogExtension> {
    implementation = "com.github.megatronking.stringfog.xor.StringFogImpl"
    enable = false
    fogPackages = arrayOf("com.fosstool.app.ui")
    kg = com.github.megatronking.stringfog.plugin.kg.RandomKeyGenerator()
    mode = com.github.megatronking.stringfog.plugin.StringFogMode.base64
}

fun getAppCenterSecret(): String {
    val secret = rootProject.file(".secret/APP_CENTER_SECRET")
    return if (secret.isFile) secret.readLines().lastOrNull().orEmpty() else ""
}
