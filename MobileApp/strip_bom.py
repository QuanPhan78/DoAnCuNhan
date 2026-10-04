import os
import codecs

def remove_bom(file_path):
    with open(file_path, "rb") as f:
        raw = f.read()
    if raw.startswith(codecs.BOM_UTF8):
        raw = raw[3:]
    text = raw.decode("utf-8")
    # also remove any internal BOMs if they exist
    text = text.replace('\ufeff', '')
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

remove_bom("lib/main.dart")
remove_bom("test/widget_test.dart")