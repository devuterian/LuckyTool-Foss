#!/usr/bin/env bash
# Sign the Korean APK without exposing its private key in Git or public artifacts.
set -euo pipefail
umask 077
VERSION="${1:?Usage: sign-release.sh VERSION}"
[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+-ko\.[0-9]+$ ]] || { echo 'Invalid release version'; exit 1; }
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
TOOLS="${ANDROID_HOME:?}/build-tools/36.0.0"
PRIVATE="${RUNNER_TEMP:?}/foss-korean-signing"
mkdir -p "$PRIVATE" dist recovery-artifact
KEYSTORE="$PRIVATE/foss-korean.p12"
trap 'rm -rf "$PRIVATE"' EXIT

if [[ -n "${ANDROID_KEYSTORE_BASE64:-}" ]]; then
  : "${ANDROID_KEYSTORE_PASSWORD:?Missing keystore password}"
  : "${ANDROID_KEY_ALIAS:?Missing key alias}"
  : "${ANDROID_KEY_PASSWORD:?Missing key password}"
  printf '%s' "$ANDROID_KEYSTORE_BASE64" | base64 --decode > "$KEYSTORE"
  export KOREAN_STORE_PASSWORD="$ANDROID_KEYSTORE_PASSWORD"
  export KOREAN_KEY_PASSWORD="$ANDROID_KEY_PASSWORD"
  KEY_ALIAS="$ANDROID_KEY_ALIAS"
else
  # Only the first Korean release may generate a key. Future releases must reuse it.
  [[ "$VERSION" == '2.0.3-ko.1' ]] || { echo 'Configure release signing secrets first.'; exit 1; }
  PREVIOUS="$(gh api "repos/$GITHUB_REPOSITORY/releases?per_page=100" --jq '.[] | select(.tag_name | contains("-ko.")) | .tag_name')"
  [[ -z "$PREVIOUS" ]] || { echo 'A Korean release already exists. Refusing to replace its signing identity.'; exit 1; }
  export KOREAN_STORE_PASSWORD="$(openssl rand -hex 32)"
  export KOREAN_KEY_PASSWORD="$KOREAN_STORE_PASSWORD"
  echo "::add-mask::$KOREAN_STORE_PASSWORD"
  KEY_ALIAS='foss-korean'
  keytool -genkeypair -keystore "$KEYSTORE" -storetype PKCS12 \
    -storepass:env KOREAN_STORE_PASSWORD -keypass:env KOREAN_KEY_PASSWORD \
    -alias "$KEY_ALIAS" -keyalg RSA -keysize 3072 -validity 10000 \
    -dname 'CN=FossTool Korean Edition, OU=devuterian'
  export RECOVERY_PRIVATE_DIR="$PRIVATE"
  python3 - <<'PY'
import base64, json, os, pathlib, zipfile
p = pathlib.Path(os.environ['RECOVERY_PRIVATE_DIR'])
key = (p / 'foss-korean.p12').read_bytes()
password = os.environ['KOREAN_STORE_PASSWORD']
secrets = {
    'ANDROID_KEYSTORE_BASE64': base64.b64encode(key).decode(),
    'ANDROID_KEYSTORE_PASSWORD': password,
    'ANDROID_KEY_ALIAS': 'foss-korean',
    'ANDROID_KEY_PASSWORD': password,
}
with zipfile.ZipFile(p / 'signing-backup.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('foss-korean.p12', key)
    z.writestr('github-secrets.json', json.dumps(secrets, indent=2))
    z.writestr('keystore.properties', 'storeFile=foss-korean.p12\nkeyAlias=foss-korean\nkeyPassword=' + password + '\nstorePassword=' + password + '\n')
    z.writestr('README.ko.txt', 'FossTool 한국어판의 비공개 APK 서명 키입니다.\n공개 저장소, 릴리스, 이슈에 올리지 마세요.\n업데이트 APK도 같은 키로 서명해야 기존 앱 위에 설치할 수 있습니다.\nGitHub 저장소 Settings > Secrets and variables > Actions에서 github-secrets.json의 네 항목을 각각 등록하세요.\n로컬 빌드에서는 이 파일들을 keystore 폴더에 보관하세요.\n')
PY
  # Encrypt before upload. Only the offline owner-held recovery private key can open it.
  EXPECTED='f2b3d977e9d9479c6719f108bf7bfcd0570acbd5927a19a1ed59d84904af1c70'
  ACTUAL="$(openssl x509 -in ci/signing-recovery-public.crt -outform DER | sha256sum | cut -d' ' -f1)"
  [[ "$ACTUAL" == "$EXPECTED" ]] || { echo 'Recovery certificate checksum mismatch'; exit 1; }
  openssl cms -encrypt -aes-256-cbc -binary -in "$PRIVATE/signing-backup.zip" \
    -outform DER -out recovery-artifact/signing-backup.p7m \
    -recip ci/signing-recovery-public.crt \
    -keyopt rsa_padding_mode:oaep -keyopt rsa_oaep_md:sha256
fi

echo "::add-mask::$KOREAN_STORE_PASSWORD"
echo "::add-mask::$KOREAN_KEY_PASSWORD"
UNSIGNED="app/build/outputs/apk/release/FossTool_${VERSION}_release.apk"
[[ -s "$UNSIGNED" ]] || { echo 'Expected release APK is missing'; exit 1; }
"$TOOLS/zipalign" -P 16 -f 4 "$UNSIGNED" "$PRIVATE/aligned.apk"
APK="dist/FossTool_${VERSION}.apk"
"$TOOLS/apksigner" sign --ks "$KEYSTORE" --ks-key-alias "$KEY_ALIAS" \
  --ks-pass env:KOREAN_STORE_PASSWORD --key-pass env:KOREAN_KEY_PASSWORD \
  --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true \
  --out "$APK" "$PRIVATE/aligned.apk"
"$TOOLS/apksigner" verify --verbose --print-certs "$APK" | tee dist/SIGNATURE.txt
"$TOOLS/zipalign" -c -P 16 4 "$APK"
"$TOOLS/aapt2" dump configurations "$APK" | grep -Eq '^ko($|-)'
[[ "$(apkanalyzer manifest debuggable "$APK")" == 'false' ]] || { echo 'Release APK is debuggable'; exit 1; }
unzip -p "$APK" assets/xposed_init | grep -q 'com.fosstool.app'
"$TOOLS/aapt2" dump badging "$APK" > dist/APK-METADATA.txt
COMMIT="$(git rev-parse HEAD)"
git archive --format=zip --prefix="FossTool-${VERSION}/" -o "dist/FossTool_${VERSION}_source.zip" "$COMMIT"
printf 'Version: %s\nSource commit: %s\nBuild run: https://github.com/%s/actions/runs/%s\n' \
  "$VERSION" "$COMMIT" "$GITHUB_REPOSITORY" "$GITHUB_RUN_ID" > dist/BUILD-INFO.txt
(cd dist && sha256sum *.apk *_source.zip > SHA256SUMS.txt)
echo 'Release signature, ZIP alignment, Korean resources, non-debuggable flag and Xposed entry point verified.'
