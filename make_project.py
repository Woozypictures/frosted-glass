import os, sys, re, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapping import MAP
from make_device_icons import make_icons as make_device_icons
from xml.sax.saxutils import escape

B = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(B, "proj")
shutil.rmtree(P, ignore_errors=True)
for d in ["res/drawable-nodpi", "res/xml", "res/values", "assets", "src/com/woozypictures/frostedglass"]:
    os.makedirs(os.path.join(P, d))

VTAG = "_v11"
def dn(pkg):
    return "ic_" + re.sub(r"[^a-z0-9]", "_", pkg.lower()) + VTAG

make_device_icons()  # regenerate device-specific glass icons before packaging
for f in os.listdir(os.path.join(B, "icons")):
    shutil.copy(os.path.join(B, "icons", f), os.path.join(P, "res/drawable-nodpi", f[:-4] + VTAG + ".png"))
shutil.copy(os.path.join(B, "drawer.png"), os.path.join(P, "res/drawable-nodpi/ic_app_drawer" + VTAG + ".png"))
shutil.copy(os.path.join(B, "appicon.png"), os.path.join(P, "res/drawable-nodpi/app_icon" + VTAG + ".png"))

comps = [l.strip() for l in open(os.path.join(B, "components.txt")) if l.strip()]
items = []
for c in comps:
    pkg, act = c.split("/", 1)
    if act.startswith("."):
        act = pkg + act
    items.append(f'    <item component="ComponentInfo{{{escape(pkg)}/{escape(act)}}}" drawable="{dn(pkg)}" />')
items.append('    <item component="ComponentInfo{com.woozypictures.frostedglass/com.woozypictures.frostedglass.MainActivity}" drawable="app_icon_v11" />')
appfilter = ('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
             '    <iconback img1="iconback_v10" />\n    <scale factor="0.5" />\n'
             + "\n".join(items) + "\n</resources>\n")
open(os.path.join(P, "res/xml/appfilter.xml"), "w").write(appfilter)
open(os.path.join(P, "assets/appfilter.xml"), "w").write(appfilter)

names = sorted(MAP, key=lambda p: MAP[p][0].lower())
drawable = ('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <version>1</version>\n    <category title="All" />\n'
            + '    <item drawable="ic_app_drawer' + VTAG + '" />\n' + "\n".join(f'    <item drawable="{dn(p)}" />' for p in names) + "\n</resources>\n")
open(os.path.join(P, "res/xml/drawable.xml"), "w").write(drawable)
open(os.path.join(P, "assets/drawable.xml"), "w").write(drawable)

open(os.path.join(P, "res/values/strings.xml"), "w").write(
    '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <string name="app_name">Frosted Glass Icon Pack</string>\n    <string name="theme_title">Frosted Glass Icon Pack</string>\n    <string name="theme_author">Woozypictures</string>\n    <string name="developer_name">Woozypictures</string>\n    <string name="app_owner">Mahesh Sharma</string>\n    <string name="copyright">App assembled and maintained by Woozypictures for Mahesh Sharma. Third-party artwork remains the property of its respective rights holders.</string>\n</resources>\n')

actions = ["org.adw.launcher.THEMES", "com.gau.go.launcherex.theme", "com.novalauncher.THEME",
           "com.teslacoilsw.launcher.THEME", "com.fede.launcher.THEME_ICONPACK", "com.anddoes.launcher.THEME",
           "com.dlto.atom.launcher.THEME", "ginlemon.smartlauncher.THEMES", "com.lge.launcher2.THEME",
           "com.tsf.shell.themes", "ch.deletescape.lawnchair.ICONPACK", "app.lawnchair.icons.THEMED_ICON"]
filters = "\n".join(f'''            <intent-filter>
                <action android:name="{a}" />
                <category android:name="android.intent.category.DEFAULT" />
            </intent-filter>''' for a in actions)
open(os.path.join(P, "AndroidManifest.xml"), "w").write(f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.woozypictures.frostedglass" android:versionCode="14" android:versionName="2.3">
    <uses-sdk android:minSdkVersion="21" android:targetSdkVersion="34" />
    <application android:label="@string/app_name" android:icon="@drawable/app_icon_v11" android:allowBackup="true">
        <meta-data android:name="author" android:value="Woozypictures" />
        <meta-data android:name="owner" android:value="Mahesh Sharma" />
        <activity android:name=".MainActivity" android:exported="true" android:label="@string/app_name" android:theme="@android:style/Theme.DeviceDefault.Wallpaper.NoTitleBar">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
{filters}
        </activity>
    </application>
</manifest>
''')

def jarr(xs):
    return ", ".join('"' + x.replace('\\', '\\\\').replace('"', '\\"') + '"' for x in xs)
tpl = open(os.path.join(B, "MainActivity.java.tpl")).read()
tpl = tpl.replace("/*LABELS*/", jarr([MAP[p][0] for p in names]))
tpl = tpl.replace("/*DRAWABLES*/", jarr([dn(p) for p in names]))
tpl = tpl.replace("/*PACKAGES*/", jarr(names))
open(os.path.join(P, "src/com/woozypictures/frostedglass/MainActivity.java"), "w").write(tpl)
print("components", len(items), "icons", len(MAP))
