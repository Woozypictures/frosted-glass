# Frosted Glass Icon Pack — Woozypictures edition

**Owner:** Mahesh Sharma  
**Developer:** Woozypictures  
**Android application ID:** `com.woozypictures.frostedglass`  
**Version:** 2.3 (versionCode 14)

**App credit:** Assembled and maintained by Woozypictures for Mahesh Sharma. This app credit does not claim ownership of third-party icon artwork; artwork remains subject to the rights and permissions of its respective creators.

This is the merged Android source project. It combines the original glass icon library supplied for this project with the custom icons Claude generated.

## What is included

See `CLAUDE_HANDOFF.md` for the identity and merge summary, and `SIGNING_IDENTITY.txt` for the public certificate fingerprint. The private signing keystore is supplied separately and is not inside this ZIP.

- `proj/` — Android app source, manifest, resources, launcher mappings and gallery.
- `icons/` — Claude's original generated icon source files (unmatched designs retained).
- `source_assets/Glass_Icon_Pack_Extracted.zip` — original glass icon pack archive, included to make the merge reproducible.
- `mapping.py`, `components.txt`, `render.py`, `MainActivity.java.tpl`, `make_project.py` — source and project-generation files.
- `merge_original_glass_pack.py` — reproducibly merges the original library into a freshly generated base project.
- `MERGE_REPORT.md` — counts and merge notes.

The merged app-filter includes the original icon pack's app mappings and the Claude project's additional launcher components. Where both projects cover the same app package, the original glass artwork takes precedence. Claude-only artwork remains available in the picker and gallery. All launcher/gallery icon canvases are normalized to 192×192 px: the original 169×169 px icons are upscaled with Lanczos resampling, preserving proportions and transparency without cropping. The untouched original ZIP remains in `source_assets/` as provenance.

## Rebuilding the merged source project

Install Pillow first (`python3 -m pip install Pillow`). Run from this directory:

```sh
python3 make_project.py
python3 merge_original_glass_pack.py
```

This regenerates `proj/` and then applies the complete original icon library. The merge uses versioned `_v11` drawable names to avoid launcher icon-cache problems.

## Building and signing

For a Windows PC with Android Studio and Android SDK Build-Tools installed, run `BUILD_APK_WINDOWS.ps1` from PowerShell at this folder. It will locate the installed SDK platform/build-tools, ask for the separate Woozypictures keystore path, prompt for its password through Android SDK tools, build the APK, sign it, and verify the signature. Example:

```powershell
.\BUILD_APK_WINDOWS.ps1 -KeystorePath "C:\path\to\Woozypictures_Release_Keystore_New.jks"
```

On Linux/macOS with Android SDK Build-Tools installed, run `./BUILD_APK_LINUX.sh /path/to/Woozypictures_Release_Keystore_New.jks`. Both scripts use the existing application ID and release alias. They do not embed or save the keystore password.


This source archive does not include a pre-signed APK or a private signing key. The previous APK and keystore were deliberately excluded because they were associated with the previous app identity.

Install Android build tools and provide your own Android 23 platform jar. The original build flow used these tools: `aapt`, `javac`, `dalvik-exchange`, `zipalign`, and `apksigner`.

Example build flow (adjust `ANDROID_JAR` for your SDK installation):

```sh
cd proj
ANDROID_JAR="$ANDROID_HOME/platforms/android-23/android.jar"
mkdir -p obj gen

aapt package -f -m -J gen -M AndroidManifest.xml -S res -A assets -I "$ANDROID_JAR" -F ../unsigned.apk
javac -source 8 -target 8 -bootclasspath "$ANDROID_JAR" -d obj -sourcepath src:gen src/com/woozypictures/frostedglass/MainActivity.java
dalvik-exchange --dex --output=classes.dex obj
aapt add ../unsigned.apk classes.dex
cd ..
zipalign -f -p 4 unsigned.apk aligned.apk
```

Sign with the separate Woozypictures release keystore supplied to the owner. Keep that keystore and its password private; do not commit them to source control or upload them to third parties:

```sh
apksigner sign --ks /secure/path/woozypictures-release.jks \
  --ks-key-alias woozypictures-release \
  --out Frosted_Glass_Icon_Pack.apk aligned.apk
```

The new application ID and signing key create a separate Android app identity. Android will not treat it as an update to an installation signed under the old key/package ID.

### Woozypictures package namespace

The active app-filter entries, fully qualified activity names, component list, gallery package index and base icon mapping have been migrated to the Woozypictures namespace. The icon pack's own mapping is `com.woozypictures.frostedglass`. Companion-app entries will match only apps that are installed with the corresponding Woozypictures package IDs. The original source archive is kept unchanged as an archival backup; the merge script applies the namespace migration during regeneration.


## Device-matched icon updates (version 2.2)

The app-filter now includes launcher components confirmed on Mahesh's phone and tablet. Twelve new custom glass icons were added for Edits, Brawlhalla, Bright Memory Infinite, Epic Games, GameNative, Old School RuneScape, Pizza Boy GBA Pro, Papa Johns, Prince of Persia: The Lost Crown, Sky: Children of the Light, X1 Box and SpongeBob BFBB. Existing Alexa and Roblox artwork is reused with updated activity aliases. Epic Games uses the confirmed tablet package and activity `com.epicgames.portal/.ui.MainActivity` (the earlier `com.epicgames.ega` guess was not installed).


## Version 2.3 (11 November 2026)

- New frosted-glass icons for Woozypictures' own apps: HQ (`uk.woozy.hq/.MainActivity`, four dashboard tiles) and HQ Fit (`uk.woozy.fit/.MainActivity`, a dumbbell). Generated by `make_device_icons.py`, mapped in `mapping.py` and `components.txt`.
- About panel (tap ABOUT in the header): Created by Woozypictures, the app version, and the Instagram, YouTube and X links.
- The gallery grid now fits its column count to the screen (about 80 dp a cell: 4 on the phone, about 15 on the tablet in landscape), so a tablet in landscape shows more icons instead of four huge ones.
- Regenerating with `make_project.py` then `merge_original_glass_pack.py` gives the 2.2 project plus exactly these two mappings, two drawables and two gallery entries; no other artwork changed.
- Build and sign exactly as before with the Woozypictures release keystore (alias `woozypictures-release`). It installs as an update over 2.2.
