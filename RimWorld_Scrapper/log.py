def log_find(log, start, end, index=1):
    """finds string between start and end by index."""
    s = 0
    for _ in range(index):
        s = log.find(start, s) + len(start)
        e = log.find(end, s)
        #print(_, s, e, log[s:e])
        result = log[s:e]
        s += e-s
    return result

class assembly:
    def __init__(self, mod_packageId, mod_name, name, version):
        self.mod_packageId = mod_packageId
        self.mod_name = mod_name
        self.name = name
        self.version = version
        self.patches = []

class MOD:
    def __init__(self, packageId = None, name = None, version = None, assemblies = []):
        self.packageId = packageId
        self.name = name
        self.version = version
        self.assemblies = assemblies

class log_RimWorld:
    def __init__(self, path = None, text = None):
        if text is None:
            with open(path, 'r', encoding='utf-8') as f:
                self.text = f.read()
        else: self.text = text

        # parse
        lines = text.split('\n')
        self.version = None
        self.warnings = []
        self.errors = []
        self.mods = []
        Initializing = False
        for i in lines:
            if Initializing is True: 
                if not i.startswith('  - '): 
                    Initializing = False
                    break
                self.mods.append(MOD(packageId = i[4:]))
            elif i == 'Initializing new game with mods:' and len(self.mods) == 0: Initializing = True
            elif i.startswith('RimWorld ') and self.version is None: 
                self.version = i[len('RimWorld '):]

class log_HugsLib(log_RimWorld):
    def __init__(self, path = None, text = None):
        if text is None:
            with open(path, 'r', encoding='utf-8') as f:
                self.text = f.read()
        else: self.text = text

        # parse
        lines = text.split('\n')
        self.version = None
        self.warnings = []
        self.errors = []
        self.mods = []
        Initializing = False
        for i in lines:
            if Initializing is True: 
                if i == '':
                    Initializing = False
                    break
                sep1 = '):' if '):' in i else   ']:'
                name_id = i[:i.rfind(sep1)+1]
                packageId = name_id[name_id.rfind('(')+1:name_id.rfind(')')].lower()
                version = name_id[name_id.rfind('['):-1] if sep1 == ']:' else None
                name = name_id[:name_id.rfind('(')]
                assemblies = i[len(name_id)+1:].split(', ')
                if assemblies[0] == '(no assemblies)': assemblies = []
                else: 
                    for j in range(len(assemblies)): assemblies[j] = assembly(mod_packageId=packageId, mod_name=name, name = assemblies[j][:assemblies[j].find('(')], version=assemblies[j][assemblies[j].find('(')+1:-1])
                self.mods.append(MOD(packageId = packageId, name = name, version = version, assemblies = assemblies))
            
            elif i == 'Loaded mods:': Initializing = True
            elif i.startswith('RimWorld ') and self.version is None: 
                self.version = i[len('RimWorld '):]

def load_log(path = None, text = None):
    if text is None:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    if text.startswith('Log uploaded'): return log_HugsLib(path = None, text = text)
    else: return log_RimWorld(path = None, text = text)

def download_from_gist_github(query, pages = 3):
    from . import GistGithub as GG
    return [load_log(text = i) for i in GG.download_logs(query=query, pages=pages)]

def find_sus_mods(error, pages = 10, exact = True):
    if exact is True and not (error.startswith('"') and error.endswith('"')): error = '"' + error + '"'
    logs = download_from_gist_github(query=error, pages=pages)
    counter = {}
    for log in logs:
        for mod in log.mods:
            if mod.packageId not in counter: counter[mod.packageId] = [mod, 1]
            else: counter[mod.packageId][1] += 1
    number = 1
    print('\nTOP100 SUSPECTS:\n')
    for i in reversed(list(sorted(counter.items(), key = lambda x: x[1][1]))):
        print(f'{i[1][1]}/{len(logs)}', i[1][0].name, i[1][0].packageId)
        number += 1
        if number == 100: break
    return counter
