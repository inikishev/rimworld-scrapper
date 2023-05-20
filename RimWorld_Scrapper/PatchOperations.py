from lxml import etree as ET

def xpath_process(xpath):
    if xpath.startswith('Defs/'): return xpath[5:]
    if xpath.startswith('/Defs/'): return xpath[6:]
    return xpath

def PatchOperationAdd(src: ET.ElementTree, xpath: str, value: str):
    xpath = xpath_process(xpath)
    if isinstance(value, str): value = ET.fromstring(value)
    for i in src.iterfind(xpath):
        i.append(ET.fromstring(ET.tostring(value)))
    return src

def PatchOperationRemove(src: ET.ElementTree, xpath: str):
    xpath = xpath_process(xpath)
    for i in src.iterfind(xpath): i.getparent().remove(i)
    return src

def PatchOperationReplace(src: ET.ElementTree, xpath: str, value: str):
    xpath = xpath_process(xpath)
    if isinstance(value, str): value = ET.fromstring(value)
    for i in src.iterfind(xpath):
        i.addnext(ET.fromstring(ET.tostring(value)))
        i.getparent().remove(i)
    return src

src = ET.fromstring('<Defs><ThingDef><defName>1</defName><i>1</i></ThingDef><ThingDef><defName>2</defName><i>1</i></ThingDef><ThingDef><defName>1</defName><i>3</i></ThingDef></Defs>')

print(ET.tostring(src))
src = PatchOperationReplace(src, 'Defs/ThingDef/i', '<BigChungus>1</BigChungus>')
print(ET.tostring(src))