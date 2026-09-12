# FossTool 한국어판

LuckyTool-Foss 2.0.3을 바탕으로 앱의 사용자 화면을 한국어로 다듬은 버전입니다. 패키지 이름은 원본과 같은 `com.fosstool.app`이며, 앱에는 **FossTool**로 표시됩니다.

[한국어판 다운로드](https://github.com/devuterian/LuckyTool-Foss/releases) · [원본 저장소](https://github.com/Qing0721/LuckyTool-Foss) · [English](README_EN.md) · [원본 소개](README.upstream.md)

## 달라진 점

설정 이름, 기능 설명, 경고, 팝업, 선택 목록, 빠른 설정 타일, 앱별 설정을 한국어로 번역했습니다. 기존 사용자용 문자열 **1,038개**와 코드에 직접 들어 있던 배터리 정보·오류 안내 등 **24개**를 한국어 리소스로 정리했습니다. 제품명, 개발자 이름, 패키지 이름, 명령어와 설정 식별자는 바꾸지 않습니다.

처음 실행하면 한국어를 사용합니다. **설정 → 언어**에서 시스템 설정 따르기나 다른 언어를 선택할 수 있으며, 이후에는 선택한 언어를 유지합니다. Android 13 이상에서는 시스템의 앱별 언어 설정과도 연동됩니다.

상태 표시줄 시계의 연·월·일, 시간대, 전통 시각과 음력 표시도 한국어 시스템 환경에 맞췄습니다. 음력 날짜 계산 자체는 기존 ColorOS 알고리즘을 그대로 사용하며, 한국천문연구원 역법으로 교체한 것은 아닙니다.

번역 때문에 기능 설정의 저장 키나 기본 활성화 상태를 변경하지 않았습니다. 기존의 위험도가 높은 옵션이 새로 자동 활성화되지 않습니다.

## 설치 전 확인

이 앱은 일반적인 독립 실행형 설정 앱이 아니라 **ColorOS 계열 기기용 LSPosed/Xposed 모듈**입니다. 원본 프로젝트는 ColorOS 15 이상을 권장합니다. APK의 설치 최소 버전은 Android 11이지만, 각 기능의 실제 작동 여부는 제조사·OS 버전·적용 대상 앱 버전에 따라 다릅니다.

**한국어판은 원본과 다른 서명 키를 사용합니다.** 기존 FossTool 위에 설치할 때 서명 충돌이 발생할 수 있습니다. 기존 앱의 설정에서 데이터를 백업한 뒤, 필요한 경우 기존 앱을 직접 제거하고 한국어판을 설치하세요. 이 저장소의 배포 도구가 사용자의 앱이나 데이터를 자동으로 삭제하지는 않습니다.

설치 후 LSPosed에서 FossTool 모듈과 필요한 적용 대상을 선택하고, 기기 또는 해당 프로세스를 다시 시작하세요. 백업이 있다면 앱의 데이터 복원 기능으로 불러오고 기능별 설정을 확인하세요.

서명 검증 해제, 보안 표시 숨기기, 온도 제한 해제 등의 기능은 기기 보안과 안정성에 영향을 줄 수 있습니다. 번역 문구와 무관하게 필요한 기능만 선택해서 사용하세요.

## 검증 범위

빌드 과정에서 번역 누락·중복, `%1$s` 같은 서식 인자, 리소스 참조, XML 형식과 언어 설정을 검사합니다. 릴리스 APK는 서명과 정렬, 한국어 리소스 포함 여부, 디버그 비활성화, Xposed 진입점도 검사합니다. 빌드 결과와 테스트 결과는 [Actions](https://github.com/devuterian/LuckyTool-Foss/actions)에서 확인할 수 있습니다.

에뮬레이터의 앱 실행 확인은 실제 ColorOS 기기에서 각 후킹 기능을 검증하는 것과 다릅니다. 실제 기기의 전체 기능 검증을 마친 버전으로 보증하지 않습니다.

## 직접 빌드

JDK 17, Gradle Wrapper, Android SDK Platform **37.0**이 필요합니다. 현재 SDK 패키지 이름은 `platforms;android-37.0`이며 `platforms;android-37`이 아닙니다. 빌드용 SDK와 별도로 앱의 `targetSdk`는 기존과 같은 36을 유지합니다.

```sh
sdkmanager 'platforms;android-37.0' 'build-tools;36.0.0'
python3 localization/generate.py --check
python3 localization/test_localization.py
bash gradlew --no-daemon --no-configuration-cache :app:assembleRelease
```

서명 설정이 없으면 릴리스 APK는 서명 없이 만들어집니다. 디버그 빌드는 개발용 서명 키를 사용합니다. 공식 한국어판과 동일한 서명이 필요한 업데이트 빌드는 반드시 보관한 한국어판 서명 키를 사용하세요.

## 번역 수정

`localization/ko/*.tsv`가 번역 원본입니다. 첫 열은 기존 리소스 이름, 두 번째 열은 한국어 문구입니다. `\n`과 서식 인자는 유지해야 합니다.

```sh
python3 localization/generate.py
python3 localization/generate.py --check
python3 localization/test_localization.py
```

생성된 `values-ko/strings.xml`과 `values-ko/arrays.xml`도 함께 커밋합니다. 별도로 추출한 실행 중 문구는 `values/runtime_strings.xml`과 `values-ko/runtime_strings.xml`에서 관리합니다.

## 릴리스 서명 키 보관

최초 한국어판 릴리스에서 생성한 개인 서명 키는 공개 저장소나 릴리스에 올리지 않습니다. 복구용 공개 인증서로 암호화한 백업만 Actions 산출물에 저장합니다. 복호화된 백업은 소유자가 비공개로 보관해야 합니다.

다음 버전부터는 저장소의 Actions Secrets에 `ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`를 등록하세요. 기존 한국어판 릴리스가 있는데 키가 없으면 배포 스크립트는 새 키를 임의로 만들지 않고 중단합니다.

## 출처와 라이선스

원본 LuckyTool-Foss 및 LuckyTool의 개발자·기여자 표기와 GNU GPL v3 라이선스를 유지합니다. 한국어판은 원 개발자의 공식 한국어판을 자칭하지 않습니다. 소스 코드는 릴리스 태그와 소스 ZIP으로 함께 제공합니다. 자세한 조건은 [LICENSE](LICENSE)를 확인하세요.
