#!/usr/bin/env python3
"""Merge the bundled original Glass icon library into the Woozypictures project.

Run after make_project.py. The script is intentionally deterministic and can be
rerun after rebuilding the base project.
"""
from pathlib import Path
import re, shutil, zipfile, tempfile, xml.etree.ElementTree as ET
from PIL import Image

ROOT = Path(__file__).resolve().parent
PROJ = ROOT / 'proj'
SOURCE_ZIP = ROOT / 'source_assets' / 'Glass_Icon_Pack_Extracted.zip'
PKG = 'com.woozypictures.frostedglass'
TAG = '_v11'

if not PROJ.exists() or not SOURCE_ZIP.exists():
    raise SystemExit('Run make_project.py first and ensure source_assets/Glass_Icon_Pack_Extracted.zip exists.')


def component_package(value):
    m = re.search(r'ComponentInfo\{([^/]+)/', value or '')
    return m.group(1) if m else None


def pretty_label(name):
    # Make source icon identifiers readable in the in-app gallery.
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    s = re.sub(r'[_\-]+', ' ', s).strip()
    return s.title() if s else name

with tempfile.TemporaryDirectory(prefix='glass-pack-') as td:
    td = Path(td)
    with zipfile.ZipFile(SOURCE_ZIP) as z:
        z.extractall(td)
    src = td / 'Glass_Icon_Pack_Extracted'
    icon_dir = src / 'icons'
    friend_appfilter = ET.parse(src / 'metadata' / 'appfilter.xml').getroot()
    friend_drawable = ET.parse(src / 'metadata' / 'drawable.xml').getroot()

    # The Glass Icon Pack project has been acquired and rebranded. Update app
    # package IDs and their fully-qualified activity names in the active mappings.
    # Its own package uses this project's current application ID; companion
    # AppsLab package IDs retain their suffix under the Woozypictures namespace.
    def rebrand_component(value):
        m = re.fullmatch(r'ComponentInfo\{([^/]+)/([^}]+)\}', value or '')
        if not m:
            return value
        old_pkg, activity = m.groups()
        if old_pkg.startswith('com.appslab.'):
            new_pkg = PKG if old_pkg == 'com.appslab.glass.iconpack' else old_pkg  # companion apps keep their real installed IDs
            if activity == old_pkg:
                activity = new_pkg
            elif activity.startswith(old_pkg + '.'):
                activity = new_pkg + activity[len(old_pkg):]
            old_pkg = new_pkg
        return f'ComponentInfo{{{old_pkg}/{activity}}}'

    for item in friend_appfilter.iter('item'):
        if 'component' in item.attrib:
            item.attrib['component'] = rebrand_component(item.attrib['component'])

    res_draw = PROJ / 'res' / 'drawable-nodpi'
    # Android resource identifiers must be lowercase. The source filenames are
    # already valid; append a version suffix so launcher caches see new artwork.
    original_files = sorted(icon_dir.glob('*.png'))
    source_names = {p.stem for p in original_files}
    name_map = {n: n.lower() + TAG for n in source_names}
    normalized_count = 0
    for p in original_files:
        target = res_draw / f'{name_map[p.stem]}.png'
        with Image.open(p) as im:
            # The source pack's main icons are 169x169 while Claude's generated
            # artwork is 192x192. Normalize the canvas to 192px without cropping
            # or changing aspect ratio; retain transparency and all other sizes.
            if im.size == (169, 169):
                im = im.resize((192, 192), Image.Resampling.LANCZOS)
                normalized_count += 1
            im.save(target, format='PNG', optimize=True)

    # Map app package names to the original artwork. This lets Claude's launcher
    # components inherit the original icon even if its activity name differs.
    package_drawable = {}
    for item in friend_appfilter.iter('item'):
        pkg = component_package(item.attrib.get('component'))
        drawable = item.attrib.get('drawable')
        if pkg and drawable in source_names:
            package_drawable.setdefault(pkg, drawable)

    # Transform all original appfilter drawable references to the versioned
    # Android resource names, dropping only the three source references whose
    # PNGs are absent from the supplied archive.
    missing_mappings = []
    for parent in friend_appfilter.iter():
        for child in list(parent):
            if child.tag == 'item' and 'drawable' in child.attrib:
                old = child.attrib['drawable']
                if old not in source_names:
                    parent.remove(child)
                    missing_mappings.append(old)
                else:
                    child.attrib['drawable'] = name_map[old]
        if parent.tag == 'iconback' and 'img1' in parent.attrib:
            old = parent.attrib['img1']
            if old in source_names:
                parent.attrib['img1'] = name_map[old]

    # Add Claude's launcher components. Where the package exists in the original
    # pack, use the original glass image; otherwise retain Claude's generated icon.
    claude_appfilter = ET.parse(PROJ / 'assets' / 'appfilter.xml').getroot()
    friend_filter = next((e for e in friend_appfilter if e.tag == 'appfilter'), None)
    if friend_filter is None:
        friend_filter = ET.SubElement(friend_appfilter, 'appfilter')
    seen_components = {
        e.attrib.get('component') for e in friend_appfilter.iter('item')
        if e.attrib.get('component')
    }
    claude_only_resources = []
    claude_resource_files = sorted(res_draw.glob(f'*{TAG}.png'))
    for item in claude_appfilter.iter('item'):
        comp = item.attrib.get('component')
        if not comp or comp in seen_components:
            continue
        pkg = component_package(comp)
        old_draw = item.attrib.get('drawable', '')
        if pkg == PKG:
            new_draw = f'app_icon{TAG}'
        elif pkg in package_drawable:
            new_draw = name_map[package_drawable[pkg]]
        else:
            new_draw = old_draw
            if new_draw.endswith(TAG):
                # Keep only Claude's unmatched custom icons in the merged picker.
                claude_only_resources.append(new_draw)
        ET.SubElement(friend_filter, 'item', {'component': comp, 'drawable': new_draw})
        seen_components.add(comp)

    # Ensure the new app's own launcher icon is represented.
    own_component = f'ComponentInfo{{{PKG}/{PKG}.MainActivity}}'
    if own_component not in seen_components:
        ET.SubElement(friend_filter, 'item', {'component': own_component, 'drawable': f'app_icon{TAG}'})

    # Remove superseded Claude package-specific PNGs; their original glass
    # equivalents now serve those packages in the appfilter.
    for pkg in package_drawable:
        replaced = 'ic_' + re.sub(r'[^a-z0-9]', '_', pkg.lower()) + TAG + '.png'
        (res_draw / replaced).unlink(missing_ok=True)

    # Build the picker list from the original categorised list, then include any
    # source images omitted from that list and Claude-only generated icons.
    drawable_root = ET.parse(src / 'metadata' / 'drawable.xml').getroot()
    listed = set()
    for item in list(drawable_root.iter('item')):
        old = item.attrib.get('drawable')
        if old:
            if old in source_names:
                item.attrib['drawable'] = name_map[old]
                listed.add(old)
            else:
                # Remove unresolved references rather than shipping broken resources.
                for parent in drawable_root.iter():
                    if item in list(parent):
                        parent.remove(item)
                        break
    all_source_items = sorted(source_names - listed)
    if all_source_items:
        category = ET.SubElement(drawable_root, 'Category', {'title': 'Additional Original Glass Icons'})
        for old in all_source_items:
            ET.SubElement(drawable_root, 'item', {'drawable': name_map[old]})
    category = ET.SubElement(drawable_root, 'Category', {'title': 'Woozypictures Custom Icons'})
    for drawable in sorted(set(claude_only_resources)):
        if (res_draw / f'{drawable}.png').exists():
            ET.SubElement(category, 'item', {'drawable': drawable})
    ET.SubElement(drawable_root, 'item', {'drawable': f'ic_app_drawer{TAG}'})
    ET.SubElement(drawable_root, 'item', {'drawable': f'app_icon{TAG}'})

    # Emit matching metadata XML files used by different icon-pack launchers.
    for path in [PROJ / 'assets' / 'appfilter.xml', PROJ / 'res' / 'xml' / 'appfilter.xml']:
        ET.indent(friend_appfilter, space='    ')
        ET.ElementTree(friend_appfilter).write(path, encoding='utf-8', xml_declaration=True)
    for path in [PROJ / 'assets' / 'drawable.xml', PROJ / 'res' / 'xml' / 'drawable.xml']:
        ET.indent(drawable_root, space='    ')
        ET.ElementTree(drawable_root).write(path, encoding='utf-8', xml_declaration=True)

    # Build a complete gallery index: all original artwork plus Claude-only art.
    package_for_drawable = {}
    for item in friend_appfilter.iter('item'):
        pkg = component_package(item.attrib.get('component'))
        draw = item.attrib.get('drawable')
        if pkg and draw:
            package_for_drawable.setdefault(draw, pkg)
    gallery = []
    for old in sorted(source_names, key=str.lower):
        gallery.append((pretty_label(old), name_map[old], package_for_drawable.get(name_map[old], 'Original Glass Library')))
    # The Claude-only package icon resources are derived from the base project arrays.
    # Keep the corresponding label/package from mapping.py when possible.
    import sys
    sys.path.insert(0, str(ROOT))
    from mapping import MAP
    for pkg, (label, _symbol) in sorted(MAP.items(), key=lambda kv: kv[1][0].lower()):
        if pkg in package_drawable:
            continue
        resname = 'ic_' + re.sub(r'[^a-z0-9]', '_', pkg.lower()) + TAG
        if (res_draw / f'{resname}.png').exists():
            gallery.append((label, resname, pkg))

    def java_array(values):
        return ', '.join('"' + str(v).replace('\\', '\\\\').replace('"', '\\"') + '"' for v in values)
    template = (ROOT / 'MainActivity.java.tpl').read_text(encoding='utf-8')
    template = template.replace('/*LABELS*/', java_array([x[0] for x in gallery]))
    template = template.replace('/*DRAWABLES*/', java_array([x[1] for x in gallery]))
    template = template.replace('/*PACKAGES*/', java_array([x[2] for x in gallery]))
    java_path = PROJ / 'src' / 'com' / 'woozypictures' / 'frostedglass' / 'MainActivity.java'
    java_path.parent.mkdir(parents=True, exist_ok=True)
    java_path.write_text(template, encoding='utf-8')

    report = f'''# Merge report\n\n- Owner: Mahesh Sharma\n- Developer: Woozypictures\n- Android application ID: `{PKG}`\n- App version: 2.3 (`versionCode` 14)\n- Original glass PNGs included: {len(source_names)}\n- Original appfilter mappings retained: {len(list(friend_appfilter.iter("item")))}\n- Claude-only custom gallery icons retained: {len(set(claude_only_resources))}\n- Gallery entries: {len(gallery)}\n- Original/Claude package overlaps resolved to original artwork: {len(set(package_drawable) & set(MAP))}\n- Missing image references in supplied original metadata omitted: {len(set(missing_mappings))}\n\nDevice-confirmed launcher components are included for Amazon Alexa (both observed aliases), Edits, Brawlhalla, Bright Memory Infinite, GameNative, Old School RuneScape, Pizza Boy GBA Pro, Roblox, Papa Johns, Prince of Persia: The Lost Crown, Sky: Children of the Light, X1 Box and SpongeBob BFBB. Twelve new custom frosted-glass icons are generated by `make_device_icons.py`. Epic Games is mapped to the tablet-confirmed launcher `com.epicgames.portal/.ui.MainActivity`. Version 2.3 adds icons for Woozypictures' own apps HQ (`uk.woozy.hq`) and HQ Fit (`uk.woozy.fit`), an About panel with the Woozypictures links, and a gallery grid that fits more columns on a tablet.\n\nThe merged project uses versioned `_v11` Android drawable resource names. The private Woozypictures signing keystore is intentionally not included. Use the same new Woozypictures release key used for the currently installed version.\n'''
    (ROOT / 'MERGE_REPORT.md').write_text(report, encoding='utf-8')
    import subprocess
    subprocess.run([sys.executable, str(ROOT / 'fix_appfilter_mappings.py'), str(ROOT)], check=True)
    print(f'Merged {len(source_names)} original PNGs; normalized {normalized_count} source icons to 192x192; gallery contains {len(gallery)} icons; package overlaps {len(set(package_drawable) & set(MAP))}.')
