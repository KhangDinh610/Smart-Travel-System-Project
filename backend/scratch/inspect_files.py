import zipfile
import xml.etree.ElementTree as ET
import json
import os

def read_xlsx_without_libs(filename):
    with zipfile.ZipFile(filename) as z:
        # Read shared strings
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            strings_xml = z.read('xl/sharedStrings.xml')
            root = ET.fromstring(strings_xml)
            # XLSX uses namespaces
            ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            for si in root.findall('ns:si', ns):
                # A shared string can have t elements, or r (rich text) runs
                t_elements = si.findall('.//ns:t', ns)
                text = "".join([t.text for t in t_elements if t.text is not None])
                shared_strings.append(text)
        
        # Read sheet1
        sheet_xml = z.read('xl/worksheets/sheet1.xml')
        root = ET.fromstring(sheet_xml)
        ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        
        rows = []
        for row in root.findall('.//ns:row', ns):
            row_data = {}
            for cell in row.findall('ns:c', ns):
                r_attr = cell.get('r') # e.g. A1, B1
                t_attr = cell.get('t') # type (s = shared string)
                val_el = cell.find('ns:v', ns)
                val = val_el.text if val_el is not None else None
                if t_attr == 's' and val is not None:
                    try:
                        val = shared_strings[int(val)]
                    except (IndexError, ValueError):
                        pass
                # Map column letter
                col_letter = "".join(filter(str.isalpha, r_attr))
                row_data[col_letter] = val
            rows.append(row_data)
        return rows

try:
    rows = read_xlsx_without_libs('phúc.xlsx')
    # Save output to a json file to avoid console encoding issues
    with open('scratch/phuc_parsed.json', 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"Successfully parsed {len(rows)} rows from phúc.xlsx and saved to scratch/phuc_parsed.json")
except Exception as e:
    import traceback
    print("Error:", e)
    traceback.print_exc()
