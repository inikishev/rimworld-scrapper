import os, random
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
comma='"'
li = lambda value, MayRequire = None, comment=None: f'<li{f" MayRequire={comma}{MayRequire}{comma}" if MayRequire is not None else ""}>{value}</li>{f" {comment}" if comment is not None else ""}'
Def_CherryPicker = lambda _Def, MayRequire = None, comment=None: li(value=f'{_Def.deftype}/{_Def.defName}', MayRequire=MayRequire, comment=comment)

from collections import Counter
def get_duplicates(array):
    c = Counter(array)
    return [k for k in c if c[k] > 1] 

class Def:
    __slots__ = 'path', 'mod_packageId', 'mod_name', 'mod_folder', 'nodes', 'deftype', 'defName', 'label', 'label_norm', 'abstract', 'parent'
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
        except Exception as e: assert False, f"KEEP MALDING: can't read {path}/About/About.xml: {e}"

        try: self.name=self.about.find('name').text
        except AttributeError: self.name = f'_{self.folder}/{random.random()}'
        try: self.packageId=self.about.find('packageId').text.lower()
        except AttributeError: 
            print(f'L: failed to get packageId from {self.folder}')
            self.packageId = f'_{self.folder}/{self.name}'

        print(f'Loading {self.name} - {self.packageId}')

        # Load all Defs
        self.Defs = set()
        #parser = ET.XMLParser(encoding='utf-8')
        for root, _, files in os.walk(path):
            if '/Defs' in root.replace('\\', '/'):
                for file in files:
                    if file.lower().endswith('.xml'):
                        try: file_xml = ET.parse(f'{root}/{file}')
                        except Exception as e:
                            print(f'F: `skipped loading {root}/{file}` due to an error: {e}')
                            continue
                            #parser = ET.XMLParser(recover=True)
                            #try: file_xml = ET.parse(f'{root}/{file}', parser=parser)
                            #except Exception as e: 
                            #    print(f'ERROR: `Unable to load {root}/{file}` - {e}')
                            #    continue
                        for _Def in file_xml.getroot():
                            self.Defs.add(Def(path = f'{root}/{file}', mod_packageId=self.packageId, mod_name=self.name, mod_folder=self.folder, nodes=_Def))
                        


    def Defs_by_type(self, types: list[str]) -> list[Def]:
        """ Returns a list of all Defs that have def types from the `types` list, e.g. all `ThingDef`"""
        if isinstance(types, 'str'): types = [types]
        return [i for i in self.Defs if i.deftype in types]
    
    def Defs_filtered(self, filter_dict: dict[str, str], rule:str = 'and') -> list[Def]:
        """Use a dictionary of key/value pairs to filter Defs. Returns a list of filtered Defs. 
        
        For example, {"label": "cow", "description": "A cow."} will filter all cows with that description."""
        if rule.lower() == 'and': return [i for i in self.Defs if all(j in i.nodes.items() for j in filter_dict.items())]
        if rule.lower() == 'or': return [i for i in self.Defs if any(j in i.nodes.items() for j in filter_dict.items())]
        assert False, f'SKILL ISSUE: `{rule}` is not a valid filter rule, it should be `and` or `or`'

class MODs:
    def __init__(self):
        self.mods = set()

    def load_MOD(self, path: str):
        """Loads ONE mod, path must be a folder that has About/About.xml or a workshop ID"""
        if all([i.isdecimal() for i in str(path)]): path = f'{WORKSHOP_LOCATION}/{path}'
        if os.path.isfile(f'{path}/About/About.xml'): 
            mod = MOD(path)
            self.mods.add(mod)
            return mod.packageId, mod.name

    def load_folder(self, path: str):
        """Loads all mods from a folder. Does NOT perform a recursive search."""
        for i in os.listdir(path): self.load_MOD(f'{path}/{i}')

    def Defs_duplicates(self, key = 'label_norm', types: list[str] = None, filter_dict: dict[str, str] = None) -> dict[str, list[Def]]: 
        """returns dictionary: `{type/key: [Def 1, Def 2, ...]}` for all Defs with identical type AND key. Type of Def is `rws.Def`.
            - `key` - Defs where this key is identical will be considered duplicates. For example, if key = "defName", all Defs with identical defNames will be found. Default value of key = "label_norm" compares by lowercase label stripped of anything but letters.
            - `types`- Search only within those def types, such as "ThingDef". Accepts a list of strings.
            - `filter_dict` - dictionary of key/value pairs to filter Defs by. For example, {"label": "cow", "description": "A cow."} will filter all cows with that description.

        Example output dictionary:
        ```
        {
            "cheetah": [AEXP_Cheetah, ACPCheetah, ...], 
            ...
        ```
        }
        """
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

    def Defs_duplicates_CherryPicker(self, output: str = True, key: str = 'label_norm', types: list[str] = None, filter_dict: dict[str, str] = None):
        """writes or returns an XML file with all duplicate Defs. 
            - `output` - path to file to write output to; if None - will only return text; if True - filename will be generated based on types.
            - `key` - Defs where this key is identical will be considered duplicates. For example, if key = "defName", all Defs with identical defNames will be found. Default value of key = "label_norm" compares by lowercase label stripped of anything but letters.
            - `types`- Search only within those def types, such as "ThingDef". Accepts a list of strings.
            - `filter_dict` - dictionary of key/value pairs to filter Defs by. For example, {"label": "cow", "description": "A cow."} will filter all cows with that description.
            
        Example output entry:
        ```xml
        <!-- cheetah -->
        <li>ThingDef/ACPCheetah</li> <!-- 2208467668/acpteam.acpvanillastyle/`Animal Collab Project Vanilla-Style` -->
        <li>ThingDef/AEXP_Cheetah</li> <!-- 2871933948/vanillaexpanded.vanillaanimalsexpanded/`Vanilla Animals Expanded -->` 
        ```"""
        space = ' '
        if output is True: output = f'{f"{space.join(types)} " if types is not None else ""}duplicates by {key}.xml'
        duplicates = sorted(list(self.Defs_duplicates(key = key, types=types, filter_dict=filter_dict).items()), key = lambda x: x[0])

        text = f'{XML_DECLARATION}\n<Duplicates>'
        newline = '\n' 
        for key, defs in duplicates: # {deftype/key: [Def 1, Def 2, ...]}
            key = key.split('/')[-1]
            text += f'\n\n<!-- {key} -->\n{newline.join([f"<li>{_Def.deftype}/{_Def.defName}</li> <!-- {_Def.mod_folder}/{_Def.mod_packageId}/`{_Def.mod_name}` -->" for _Def in defs])}'
        text+= '\n</Duplicates>'
        if output is not None:
            with open(output, 'w', encoding='utf8') as f: f.write(text)
        return text
    
    def Defs_CherryPicker(self, output: str = True, types: list[str] = None, filter_dict: dict[str, str] = None):
        """writes or returns an XML file with all Defs grouped by mod. 
            - `output` - path to file to write output to; if None - will only return text; if True - filename will be generated based on types.
            - `key` - Defs where this key is identical will be considered duplicates. For example, if key = "defName", all Defs with identical defNames will be found. Default value of key = "label_norm" compares by lowercase label stripped of anything but letters.
            - `types`- Search only within those def types, such as "ThingDef". Accepts a list of strings.
            - `filter_dict` - dictionary of key/value pairs to filter Defs by. For example, {"label": "cow", "description": "A cow."} will filter all cows with that description.
        
        Example output entry: 
        ```xml
        <!-- Quartzian Race (Continued) / zal.quartzian / 2903484599 -->
        <li>FactionDef/QuartzFaction</li> <!-- Quartzian Grotto -->
        <li>FactionDef/QuartzPlayerColony</li> <!-- Quartzians -->
        ```"""
        text = f'{XML_DECLARATION}\n<AllDefs>'
        for mod in self.mods:
            text+=(f'\n<!-- {mod.name} / {mod.packageId} / {mod.folder} -->')
            text+='\n'.join(sorted(list(set([f'<li>{i.deftype}/{i.defName}</li> <!-- {i.label} -->' for i in (mod.Defs_filtered(filter_dict) if filter_dict is not None else mod.Defs) if i.defName is not None and (i.deftype in types if types is not None else True)]))))
            text+='\n'
        text+='</AllDefs>'
        space = ' '
        if output is True: output = f'all {f"{space.join(types)} " if types is not None else ""}defs.xml'
        if output is not None: 
            with open(output, 'w', encoding='utf8') as f: f.write(text)
        return text
    
def find_duplicates(folder:str = WORKSHOP_LOCATION, key:str = 'label_norm', types: list[str] = None, filter_dict: dict[str, str] = None):
    """writes an XML file with all duplicates. 
        - `key` - Defs where this key is identical will be considered duplicates. For example, if key = "defName", all Defs with identical defNames will be found. Default value of key = "label_norm" compares by lowercase label stripped of anything but letters.
        - `types`- Search only within those def types, such as "ThingDef". Accepts a list of strings.
        - `filter_dict` - dictionary of key/value pairs to filter Defs by. For example, {"label": "cow", "description": "A cow."} will filter all cows with that description.

    Example output entry:
    ```xml
    <!-- cheetah -->
    <li>ThingDef/ACPCheetah</li> <!-- 2208467668/acpteam.acpvanillastyle/`Animal Collab Project Vanilla-Style` -->
    <li>ThingDef/AEXP_Cheetah</li> <!-- 2871933948/vanillaexpanded.vanillaanimalsexpanded/`Vanilla Animals Expanded -->` 
    ```"""
    mods = MODs()
    mods.load_folder(folder)
    mods.Defs_duplicates_CherryPicker(key=key, types = types,filter_dict=filter_dict)

def find_duplicates_between_two_mods(mod_priority: str, mod_duplicate: str, key: str = 'label_norm', types: list[str] = None, filter_dict: dict[str, str] = None):
    """Writes a CherryPicker.DefList xml file with all `mod_duplicate` duplicates of `mod_priority` Defs. Due to the @MayRequire attribute, in RimWorld the list will only be loaded if both mods are loaded.
        - `mod_priority` - path or workshop ID of the mod that takes priority
        - `mod_duplicate` - path or workshop ID of the mod, defs from which will be removed as duplicates.
        - `key` - Defs where this key is identical will be considered duplicates. For example, if key = "defName", all Defs with identical defNames will be found. Default value of key = "label_norm" compares by lowercase label stripped of anything but letters.
        - `types`- Search only within those def types, such as "ThingDef". Accepts a list of strings.
        - `filter_dict` - dictionary of key/value pairs to filter Defs by. For example, {"label": "cow", "description": "A cow."} will filter all cows with that description.
    
    Example output:
    ```xml
    <?xml version="1.0" encoding="utf-8"?>
    <Defs>
        <!-- HC_Animal_1 > Animal Collab Project Vanilla-Style -->
        <CherryPicker.DefList MayRequire="owlchemist.cherrypicker, hc.animal.1, acpteam.acpvanillastyle">
            <defName>dupes_hc_animal_1_acpteam_acpvanillastyle</defName>
            <label>HC_Animal_1 &gt; Animal Collab Project Vanilla-Style</label>
            <defs>
                <li MayRequire="hc.animal.1">PawnKindDef/ACPKomodo</li> <!--HC_KomodoDragon/KomodoDragon-->
                <li MayRequire="hc.animal.1">ThingDef/ACPKomodo</li> <!--HC_KomodoDragon/KomodoDragon-->
                <li MayRequire="hc.animal.1">ThingDef/ACPEggKomodoFertilized</li> <!--EggKomodoDragonFertilized/KomodoDragon egg (fert.)-->
            </defs>
        </CherryPicker.DefList>
    </Defs>
    ```"""
    mods = MODs()
    mod_priority,priority_name = mods.load_MOD(mod_priority)
    mod_duplicate,duplicate_name= mods.load_MOD(mod_duplicate)
    duplicates = sorted(list(mods.Defs_duplicates(key = key, types=types, filter_dict=filter_dict).items()), key = lambda x: x[0])
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

def get_all_mod_defs(folder: str, types: list[str] = None, filter_dict: dict[str,str] = None):
    """Writes a CherryPicker.DefList xml file with all Defs grouped by mod.
        - `key` - Defs where this key is identical will be considered duplicates. For example, if key = "defName", all Defs with identical defNames will be found. Default value of key = "label_norm" compares by lowercase label stripped of anything but letters.
        - `types`- Search only within those def types, such as "ThingDef". Accepts a list of strings.
        - `filter_dict` - dictionary of key/value pairs to filter Defs by. For example, {"label": "cow", "description": "A cow."} will filter all cows with that description.

    Example output entry:
    ```xml
    <!-- ↁ Elves / devdesigner.elves / 2905623211 -->
    <li>FactionDef/DevDesigner_DarkElvesFaction</li> <!-- Dark elves -->
    <li>FactionDef/DevDesigner_DarkElvesFaction_Player</li> <!-- dark elf coven -->
    <li>FactionDef/DevDesigner_HighElvesFaction</li> <!-- High elves -->
    <li>FactionDef/DevDesigner_HighElvesFaction_Player</li> <!-- high elf colony -->
    <li>FactionDef/DevDesigner_RoughDarkElvesFaction</li> <!-- rough Dark elves -->
    <li>FactionDef/DevDesigner_RoughHighElvesFaction</li> <!-- rough High elves -->
    <li>FactionDef/DevDesigner_SavageWoodElvesFaction</li> <!-- savage Wood elves -->
    <li>FactionDef/DevDesigner_WoodElvesFaction</li> <!-- Wood elves -->
    <li>FactionDef/DevDesigner_WoodElvesFaction_Player</li> <!-- wood elf clan -->
    ```
    """
    mods = MODs()
    if isinstance(folder, (list, tuple)): 
        for i in folder:
            if mods.load_MOD(i) is None: mods.load_folder(i)
    elif mods.load_MOD(folder) is None: mods.load_folder(folder)
    mods.Defs_CherryPicker(types = types, filter_dict=filter_dict)