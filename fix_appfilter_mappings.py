#!/usr/bin/env python3
"""Final app-filter corrections for Frosted Glass Icon Pack (Woozypictures).

Applied after merge_original_glass_pack.py. Safe to re-run (idempotent).
  1. Restores the real Android package IDs of the eight third-party AppsLab
     companion apps (the pack's own ID stays com.woozypictures.frostedglass).
  2. Fixes malformed ComponentInfo strings where the intended component is
     unambiguous; removes only entries that cannot be reliably corrected.
  3. Resolves components mapped to two different icons, keeping the most
     appropriate icon for each.
No artwork is touched; every icon stays in the gallery and icon picker.
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
PROJ = ROOT / 'proj'
OWN_PKG = 'com.woozypictures.frostedglass'
CI = 'ComponentInfo{%s}'

# 1. Third-party companion apps: restore the IDs the installed apps actually use.
COMPANIONS = [
    'photo.widgetspro', 'nothing.widgetspro', 'materialyou.widgetspro', 'glass.widgets',
    'game.booster.pro', 'gallery', 'watchfaces.marketplace', 'nickname.ascii.stylishtext.ff.gamers',
]

# 2a. Malformed strings whose intended app/activity is unambiguous.
SYNTAX_FIXES = {
    'omponentInfo{com.google.android.calendar/com.android.calendar.LaunchActivity}':
        CI % 'com.google.android.calendar/com.android.calendar.LaunchActivity',
}
# 2b. Malformed entries that cannot be reliably corrected (or are redundant).
REMOVE_COMPONENTS = [
    'Componentinfo{com.android.soundrecorder/com.android.soundrecorder.StartActivity}',
    # ^ miscased copy; the correctly written component already maps to the same icon
    CI % '/com.harry.wallpie.ui.activity.MainActivity',   # package name missing, not verifiable
    CI % 'missing.google.cantonese',                      # placeholder, no activity
    CI % 'missing.google.day.dream',                      # placeholder, no activity
    CI % 'com.google.android.apps.pdfviewer',             # package only, no activity
    CI % 'com.oneplus.gamespace/com.oplus.games/com.oplus.games.ui.main.MainGameActivity',
    # ^ two components fused together; both valid forms are already mapped separately
]
# ':LAUNCHER_ACTION_APP_DRAWER' is a valid launcher token (app-drawer button) and is kept.

# 3. Component -> icon to keep, where two different icons were mapped.
WINNERS = {
    'com.coloros.video/com.oppo.video.VideoListActivity': 'coloros_video_v11',
    'com.coloros.video/com.oppo.video.SplashActivity': 'coloros_video_v11',
    'com.coloros.video/com.oplus.video.VideoListActivity': 'coloros_video_v11',
    'com.coloros.video/com.oplus.video.SplashActivity': 'coloros_video_v11',
    'com.coloros.video/com.oplus.video.ui.VideoListActivity': 'coloros_video_v11',
    'com.coloros.video/com.heytap.video.splash.VideoSplashActivity': 'coloros_video_v11',
    'com.transsion.magicshow/com.transsion.magicmovie.activity.TRSplashActivity': 'visha_video_player_v11',
    'com.brouken.player/com.brouken.player.PlayerActivity': 'just_video_player_v11',
    'com.simplemobiletools.camera/com.simplemobiletools.camera.activities.SplashActivity.Orange': 'simple_camera_v11',
    'org.lineageos.jelly/org.lineageos.jelly.MainActivity': 'jelly_browser_v11',
    'twelve.clock.mibrahim/twelve.clock.mibrahim.Thebase': 'pixel_clock_v11',
    'com.google.android.dialer/com.google.android.dialer.extensions.GoogleDialtactsActivity': 'google_phone_v11',
    'com.simplemobiletools.filemanager.pro/com.simplemobiletools.filemanager.pro.activities.SplashActivity.Orange': 'simple_file_manager_pro_v11',
    'com.synology.DSfile/com.synology.DSfile.Splash': 'ds_file_v11',
    'com.standardnotes/com.standardnotes.MainActivity': 'standard_notes_v11',
    'com.simplemobiletools.notes.pro/com.simplemobiletools.notes.pro.activities.SplashActivity.Orange': 'simple_notes_pro_v11',
    'com.ytheekshana.deviceinfo/com.ytheekshana.deviceinfo.SplashActivity': 'device_info_system_cpu_info_v11',
    'com.barcode.qrcode.scanner.reader.pro/com.barcode.qrcode.scanner.reader.pro.activity.MainActivity': 'qr_code_reader_pro_v11',
    'de.wetteronline.wetterapppro/de.wetteronline.wetterapp.MainActivityGoogle': 'weather_radar_pro_v11',
    'com.asus.weathertime/com.asus.weathertime.WeatherTimeSettings': 'asus_weather_v11',
    'com.android.calendar/com.android.calendar.AllInOneActivity': 'calendar_1_v11',
    'com.android.calendar/com.android.calendar.homepage.AllInOneActivity': 'calendar_1_v11',
    'com.coloros.calendar/com.android.calendar.AllInOneActivity': 'calendar_1_v11',
    'com.motorola.cn.calendar/com.motorola.cn.calendar.AllInOneActivity': 'calendar_1_v11',
    'com.android.calendar/com.meizu.flyme.calendar.AllInOneActivity': 'calendar_1_v11',
    'com.sonymobile.calendar/com.sonymobile.calendar.LaunchActivity': 'calendar_1_v11',
    'com.motorola.dolby.dolbyui/com.motorola.dolby.dolbyui.ui.LauncherActivity': 'moto_audio_v11',
    'com.motorola.moto/com.motorola.assist.LauncherActivity': 'moto_v11',
    'com.samsung.oh/com.samsung.oh.MainActivity': 'samsung_members_v11',
    'com.heytap.cloud/com.heytap.cloud.home.ui.CloudLauncherActivity': 'heytap_cloud_v11',
    'com.heytap.cloud/com.heytap.cloud.activity.CloudSettingsActivity': 'heytap_cloud_v11',
    'com.heytap.cloud/com.heytap.cloud.activity.OPCloudSettingsActivity': 'heytap_cloud_v11',
    'com.xiaomi.hm.health/com.xiaomi.hm.health.activity.StartUpActivity': 'zepp_life_v11',
    'com.mi.globalbrowser.mini/com.miui.android.apps.chrome.Main': 'mint_browser_v11',
    'com.samsung.android.mdx/com.samsung.android.mdx.windowslink.tileservice.LinkToWidowsLauncherActivityDummy': 'samsung_link_to_windows_service_v11',
    'com.vivo.easyshare/com.vivo.easyshare.activity.SplashScreenActivity': 'vivo_easyshare_v11',
    'com.arjanvlek.oxygenupdater/com.oxygenupdater.activities.MainActivity': 'oxygen_updater_v11',
    'com.arjanvlek.oxygenupdater/com.oxygenupdater.activities.SplashActivity': 'oxygen_updater_v11',
    f'{OWN_PKG}/{OWN_PKG}.MainActivity': 'app_icon_v11',
    'com.vanced.android.apps.youtube.music/com.google.android.apps.youtube.music.activities.MusicActivity': 'youtube_music_vanced_google_v11',
}
WINNERS = {CI % k: v for k, v in WINNERS.items()}

ITEM = re.compile(r'^\s*<item component="([^"]*)" drawable="([^"]*)" />\s*$')


def fix_appfilter(text):
    log = []
    for tail in COMPANIONS:
        old, new = 'com.woozypictures.' + tail, 'com.appslab.' + tail
        n = len(re.findall(re.escape(old) + r'(?=[/.}])', text))
        if n:
            text = re.sub(re.escape(old) + r'(?=[/.}])', new, text)
            log.append(f'restored {old} -> {new} ({n} occurrences)')
    for bad, good in SYNTAX_FIXES.items():
        if f'component="{bad}"' in text:
            text = text.replace(f'component="{bad}"', f'component="{good}"')
            log.append(f'fixed syntax {bad} -> {good}')
    # Only drop a competing icon when the preferred one is actually mapped for that
    # component, so no app ever loses its only mapping.
    present = {(m.group(1), m.group(2)) for m in map(ITEM.match, text.split('\n')) if m}
    out = []
    for line in text.split('\n'):
        m = ITEM.match(line)
        if m:
            comp, draw = m.groups()
            if comp in REMOVE_COMPONENTS:
                log.append(f'removed malformed {comp} ({draw})')
                continue
            if comp in WINNERS and draw != WINNERS[comp] and (comp, WINNERS[comp]) in present:
                log.append(f'removed duplicate {comp} -> {draw} (kept {WINNERS[comp]})')
                continue
        out.append(line)
    return '\n'.join(out), log


def fix_java(text, own_uses_glass_icon):
    # Gallery package index: real companion IDs. If the old pack's glass icon is
    # no longer this app's mapping, list it like other library artwork.
    for tail in COMPANIONS:
        text = text.replace(f'"com.woozypictures.{tail}"', f'"com.appslab.{tail}"')
    m = re.search(r'static final String\[\] DRAWABLES = \{(.*?)\};', text, re.S)
    drawables = re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))
    m2 = re.search(r'(static final String\[\] PACKAGES = \{)(.*?)(\};)', text, re.S)
    packages = re.findall(r'"((?:[^"\\]|\\.)*)"', m2.group(2))
    assert len(drawables) == len(packages)
    for i, d in enumerate(drawables):
        if d == 'glass_iconpack_v11' and packages[i] == OWN_PKG and not own_uses_glass_icon:
            packages[i] = 'Original Glass Library'
    body = ', '.join('"' + p.replace('\\', '\\\\').replace('"', '\\"') + '"' for p in packages)
    return text[:m2.start(2)] + body + text[m2.end(2):]


def main():
    paths = [PROJ / 'res' / 'xml' / 'appfilter.xml', PROJ / 'assets' / 'appfilter.xml']
    for p in paths:
        new, log = fix_appfilter(p.read_text(encoding='utf-8'))
        p.write_text(new, encoding='utf-8')
    for entry in log:
        print(entry)
    java = PROJ / 'src' / 'com' / 'woozypictures' / 'frostedglass' / 'MainActivity.java'
    own_glass = f'component="ComponentInfo{{{OWN_PKG}/{OWN_PKG}.MainActivity}}" drawable="glass_iconpack_v11"' in new
    java.write_text(fix_java(java.read_text(encoding='utf-8'), own_glass), encoding='utf-8')
    print(f'{len(log)} corrections applied')


if __name__ == '__main__':
    main()
