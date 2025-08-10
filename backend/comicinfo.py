import zipfile
import rarfile
import tempfile
import shutil
import os
import xml.etree.ElementTree as ET

def get_comicinfo_date(archive_path):
    def parse_xml(xmlbytes):
        try:
            tree = ET.ElementTree(ET.fromstring(xmlbytes.decode("utf-8")))
            root = tree.getroot()
            year = root.findtext("Year")
            month = root.findtext("Month")
            day = root.findtext("Day")
            return (year, month, day)
        except Exception:
            return (None, None, None)

    if archive_path.lower().endswith(('.cbz', '.zip')):
        with zipfile.ZipFile(archive_path, 'r') as z:
            for name in z.namelist():
                if name.lower().endswith('comicinfo.xml'):
                    with z.open(name) as f:
                        return parse_xml(f.read())
    elif archive_path.lower().endswith(('.cbr', '.rar')):
        with rarfile.RarFile(archive_path, 'r') as r:
            for info in r.infolist():
                if info.filename.lower().endswith('comicinfo.xml'):
                    with r.open(info) as f:
                        return parse_xml(f.read())
    return (None, None, None)

def set_comicinfo_date(archive_path, year, month, day):
    root = ET.Element("ComicInfo")
    for tag, val in [("Year", year), ("Month", month), ("Day", day)]:
        e = ET.SubElement(root, tag)
        e.text = str(val) if val is not None else ""
    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    if archive_path.lower().endswith(('.cbz', '.zip')):
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(archive_path, 'r') as zin:
                zin.extractall(tmpdir)
            with open(os.path.join(tmpdir, "ComicInfo.xml"), "wb") as f:
                f.write(xml_bytes)
            tmpzip = archive_path + ".tmp"
            with zipfile.ZipFile(tmpzip, 'w', zipfile.ZIP_DEFLATED) as zout:
                for folder, _, files in os.walk(tmpdir):
                    for file in files:
                        fp = os.path.join(folder, file)
                        arcname = os.path.relpath(fp, tmpdir)
                        zout.write(fp, arcname)
            shutil.move(tmpzip, archive_path)
        return True

    elif archive_path.lower().endswith(('.cbr', '.rar')):
        with tempfile.TemporaryDirectory() as tmpdir:
            with rarfile.RarFile(archive_path, 'r') as rin:
                rin.extractall(tmpdir)
            with open(os.path.join(tmpdir, "ComicInfo.xml"), "wb") as f:
                f.write(xml_bytes)
            tmp_rar = archive_path + ".tmp"
            import subprocess
            subprocess.run([
                "rar", "a", "-ep1", tmp_rar, "."],
                cwd=tmpdir, check=True)
            shutil.move(tmp_rar, archive_path)
        return True

    return False