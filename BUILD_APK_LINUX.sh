#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="$ROOT/proj"
SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
KEYSTORE="${1:-}"
ALIAS="woozypictures-release"

if [[ -z "$SDK" || ! -d "$SDK" ]]; then echo 'Set ANDROID_HOME or ANDROID_SDK_ROOT to your Android SDK folder.' >&2; exit 1; fi
if [[ -z "$KEYSTORE" ]]; then read -r -p 'Path to Woozypictures_Release_Keystore_New.jks: ' KEYSTORE; fi
[[ -f "$KEYSTORE" ]] || { echo "Keystore not found: $KEYSTORE" >&2; exit 1; }
KEYSTORE="$(realpath "$KEYSTORE")"
PLATFORM="$(find "$SDK/platforms" -mindepth 2 -maxdepth 2 -name android.jar -printf '%h\n' | sort -V | tail -1)"
[[ -n "$PLATFORM" ]] || { echo 'Install an Android platform (API 23 or newer) in SDK Manager.' >&2; exit 1; }
BT="$(find "$SDK/build-tools" -mindepth 1 -maxdepth 1 -type d | sort -V | tail -1)"
[[ -n "$BT" ]] || { echo 'Install Android SDK Build-Tools in SDK Manager.' >&2; exit 1; }
ANDROID_JAR="$PLATFORM/android.jar"
WORK="$ROOT/apk_build"
mkdir -p "$WORK/gen" "$WORK/obj" "$WORK/dex"
rm -rf "$WORK/gen"/* "$WORK/obj"/* "$WORK/dex"/*

cd "$PROJECT"
"$BT/aapt" package -f -m --no-crunch -0 arsc -J "$WORK/gen" -M AndroidManifest.xml -S res -A assets -I "$ANDROID_JAR" -F "$WORK/unsigned.apk"
javac -encoding UTF-8 -source 8 -target 8 -bootclasspath "$ANDROID_JAR" -d "$WORK/obj" -sourcepath "src:$WORK/gen" src/com/woozypictures/frostedglass/MainActivity.java
jar --create --file "$WORK/classes.jar" -C "$WORK/obj" .
"$BT/d8" --release --min-api 21 --lib "$ANDROID_JAR" --output "$WORK/dex" "$WORK/classes.jar"
cp "$WORK/unsigned.apk" "$WORK/unsigned_with_dex.apk"
(cd "$WORK/dex" && "$BT/aapt" add "$WORK/unsigned_with_dex.apk" classes.dex)
"$BT/zipalign" -f -p 4 "$WORK/unsigned_with_dex.apk" "$WORK/aligned.apk"
"$BT/apksigner" sign --ks "$KEYSTORE" --ks-key-alias "$ALIAS" --out "$ROOT/Frosted_Glass_Icon_Pack.apk" "$WORK/aligned.apk"
"$BT/apksigner" verify --verbose --print-certs "$ROOT/Frosted_Glass_Icon_Pack.apk"
echo "SUCCESS: $ROOT/Frosted_Glass_Icon_Pack.apk"
