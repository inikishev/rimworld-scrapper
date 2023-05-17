import tkinter, os, random
import xml.etree.ElementTree as ET
WORKSHOP_LOCATION = 'D:/SteamLibrary/steamapps/workshop/content/294100'
XML_DECLARATION = '<?xml version="1.0" encoding="utf-8"?>'
newline = '\n'
CherryPicker_DefList = lambda s, defName, label, comment, MayRequire: f'''{XML_DECLARATION}
<Defs>{f'{newline}    <!-- {comment} -->' if comment is not None else ''}
    <CherryPicker.DefList MayRequire="owlchemist.cherrypicker, {MayRequire}">
        <defName>{defName}</defName>
        <label>{label}</label>
        <defs>
            {s}
        </defs>
    </CherryPicker.DefList>
</Defs>'''

from collections import Counter
def get_duplicates(array):
    c = Counter(array)
    return [k for k in c if c[k] > 1] 

class Def:
    def __init__(self, path, mod_packageId, mod_name, mod_folder, nodes: ET.ElementTree):
        self.path = path
        self.mod_packageId = mod_packageId
        self.mod_name = mod_name
        self.mod_folder = mod_folder
        self.nodes = nodes

        # get data
        self.deftype = nodes.tag
        defName = nodes.find('defName')
        self.defName = defName.text if defName is not None else None
        label = nodes.find('label')
        self.label = label.text if label is not None else None
        self.label_norm = (''.join(i for i in self.label if i.isalnum())).lower() if self.label is not None else None
        self.abstract = True if 'Abstract' in self.nodes.attrib and self.nodes.attrib['Abstract'] == 'True' else False
        self.parent = self.nodes.attrib['ParentName'] if 'ParentName' in self.nodes.attrib else None

class MOD:
    def __init__(self, path: str):
        if all([i.isdecimal() for i in str(path)]): path = f'{WORKSHOP_LOCATION}/{path}'
        self.path = path
        self.folder = path.replace('\\', '/').split('/')[-1]

        try: self.about=ET.parse(f'{path}/About/About.xml')
        except Exception as e: assert False, f"ERROR: can't read {path}/About/About.xml: {e}"

        try: self.name=self.about.find('name').text
        except AttributeError: self.name = f'_{self.folder}/{random.random()}'
        try: self.packageId=self.about.find('packageId').text.lower()
        except AttributeError: 
            print(f'ERROR: failed to get packageId from {self.folder}')
            self.packageId = f'_{self.folder}/{self.name}'

        print(f'Loading {self.name} - {self.packageId}')

        # Load all Defs
        self.Defs = set()
        parser = ET.XMLParser(encoding='utf-8')
        for root, _, files in os.walk(path):
            if '/Defs' in root.replace('\\', '/'):
                for file in files:
                    if file.lower().endswith('.xml'):
                        try: file_xml = ET.parse(f'{root}/{file}')
                        except Exception as e:
                            print(f'ERROR: `skipped loading {root}/{file}` due to an error: {e}')
                            continue
                            #parser = ET.XMLParser(recover=True)
                            #try: file_xml = ET.parse(f'{root}/{file}', parser=parser)
                            #except Exception as e: 
                            #    print(f'ERROR: `Unable to load {root}/{file}` - {e}')
                            #    continue
                        for _Def in file_xml.getroot():
                            self.Defs.add(Def(path = f'{root}/{file}', mod_packageId=self.packageId, mod_name=self.name, mod_folder=self.folder, nodes=_Def))
                        


    def get_by_type(self, types: list):
        """ Returns a list of all nodes in a given list of Def types, like `ThingDef`"""
        if isinstance(types, 'str'): types = [types]
        return [i for i in self.Defs if i.deftype in types]
    
    def filtered(self, filter_dict: dict, rule = 'and'):
        """Heres how you do the filter: {'label': 'cow', 'description': 'A cow.'} and rule = `and` means it will filter all cows with that description. If rule is `or` it will filter all Defs where at least one of those matches."""
        if rule.lower() == 'and': return [i for i in self.Defs if all(j in i.nodes.items() for j in filter_dict.items())]
        if rule.lower() == 'or': return [i for i in self.Defs if any(j in i.nodes.items() for j in filter_dict.items())]
        assert False, f'SKILL ISSUE: alright so basically `{rule}` is not a valid filter rule, it should be `and` or `or`'

class XMLDOC:
    def __init__(self):
        self.mods = set()

    def load_mod(self, path):
        """Loads ONE mod, path must be a folder that has About/About.xml"""
        if all([i.isdecimal() for i in str(path)]): path = f'{WORKSHOP_LOCATION}/{path}'
        if os.path.isfile(f'{path}/About/About.xml'): 
            mod = MOD(path)
            self.mods.add(mod)
            return mod.packageId, mod.name

    def load_folder(self, path):
        for i in os.listdir(path): self.load_mod(f'{path}/{i}')

    def duplicates(self, key = 'label_norm', types = None, filter_dict = None): 
        """returns dictionary: {type/key: [Def 1, Def 2, ...]} for all Defs that share type/key"""
        nodes = {}
        for mod in self.mods:

            mod_nodes = {}
            for _Def in mod.filtered(filter_dict) if filter_dict is not None else mod.Defs:
                # if def type is allowed and if key is in def nodes
                if (_Def.deftype in types if types is not None else True) and ((key in _Def.nodes) if key != 'label_norm' else (_Def.label_norm is not None)):
                    # I get a dictionary: {packageId/deftype/key: Def}, no duplicates from the same mod
                    def_key = _Def.label_norm if key == 'label_norm' else _Def.nodes[key]
                    mod_key = f'{mod.packageId}/{_Def.deftype}/{def_key}'
                    if mod_key not in mod_nodes.keys(): mod_nodes[mod_key] = _Def
                    
            # so i get unique defs from each mod and add them to all defs
            nodes |= mod_nodes

        # Now I get a list of duplicates
        duplicates_list = get_duplicates(['/'.join(i.split('/')[-2:]) for i in list(nodes.keys())])
        #print(duplicates_list)

        # I get a dictionary: {deftype/key: [Def 1, Def 2, ...]}
        duplicates = {}
        for k,v in nodes.items():
            type_key = '/'.join(k.split('/')[-2:])
            if type_key in duplicates_list:
                if type_key not in duplicates: duplicates[type_key] = [v]
                else: duplicates[type_key].append(v)
        
        return duplicates

    def duplicates_all_li(self, output = True, key = 'label_norm', types = None, filter_dict = None):
        """writes or returns an XML file with all found duplicates, in the format:
        <!-- key -->
        <li>type/defName1</li> <!-- mod1 folder/mod1 packageId/`mod1 name` -->
        <li>type/defName2</li> <!-- mod2 folder/mod2 packageId/`mod2 name` -->"""
        space = ' '
        if output is True: output = f'{f"{space.join(types)} " if types is not None else ""}duplicates by {key}.xml'
        duplicates = sorted(list(self.duplicates(key = key, types=types, filter_dict=filter_dict).items()), key = lambda x: x[0])

        text = f'{XML_DECLARATION}\n<Duplicates>'
        newline = '\n' 
        for key, defs in duplicates: # {deftype/key: [Def 1, Def 2, ...]}
            key = key.split('/')[-1]
            text += f'\n\n<!-- {key} -->\n{newline.join([f"<li>{_Def.deftype}/{_Def.defName}</li> <!-- {_Def.mod_folder}/{_Def.mod_packageId}/`{_Def.mod_name}` -->" for _Def in defs])}'
        text+= '\n</Duplicates>'
        if output is not None:
            with open(output, 'w', encoding='utf8') as f: f.write(text)
        return text
    
def get_all_duplicates(folder = WORKSHOP_LOCATION, key = 'label_norm', types = None, filter_dict = None):
    """Get all duplicates for all mods in the folder."""
    mods = XMLDOC()
    mods.load_folder(folder)
    mods.duplicates_all_li(key=key, types = types,filter_dict=filter_dict)

def CherryPicker_two_mod_duplicates(mod_priority, mod_duplicate, key = 'label_norm', types = None, filter_dict = None):
    mods = XMLDOC()
    mod_priority,priority_name = mods.load_mod(mod_priority)
    mod_duplicate,duplicate_name= mods.load_mod(mod_duplicate)
    duplicates = sorted(list(mods.duplicates(key = key, types=types, filter_dict=filter_dict).items()), key = lambda x: x[0])
    text = []
    for key, defs in duplicates: # {deftype/key: [Def 1, Def 2, ...]}
        for _Def in defs:
            if _Def.mod_packageId.lower() == mod_priority.lower():
                priority_defName = _Def.defName
                label = _Def.label
                deftype = _Def.deftype
                priority_packageId = _Def.mod_packageId
            else:
                duplicate_defName = _Def.defName
        
        if priority_defName != duplicate_defName: 
            text.append(f'<li MayRequire="{priority_packageId}">{deftype}/{duplicate_defName}</li> <!--{priority_defName}/{label}-->')
    with open(f'{mod_priority} {mod_duplicate}.xml', 'w', encoding='utf8') as f: 
        f.write(CherryPicker_DefList('\n'.join(text),  f'dupes_{mod_priority.replace(".", "_")}_{mod_duplicate.replace(".", "_")}', f'{priority_name} &gt; {duplicate_name}', f'{priority_name} > {duplicate_name}', f'{mod_priority}, {mod_duplicate}'))

#get_all_duplicates(types = ['ThingDef', 'PawnKindDef', 'RecipeDef'])
CherryPicker_two_mod_duplicates(2894599725, 2589837522)