doesn't need any libraries

## import it
```py
import RimWorld_Scrapper as rws
```

## Find duplicates between two mods:
```py
rws.find_duplicates_between_two_mods(
  mod_priority = r'D:\SteamLibrary\steamapps\workshop\content\294100\2871933948', 
  mod_duplicate = r'D:\SteamLibrary\steamapps\workshop\content\294100\2013243795', 
  types = ['ThingDef', 'PawnKindDef'])
```
It writes ready to use cherry picker XML file next to your .py file. You can just plop that file straight into your mod's Defs folder, launch the game and click on the list in cherry picker.

Duplicates are things of the same type (like ThingDef) that have the same label, also before comparison all labels are converted to lowercase and all characters except letters are removed, so no spaces. 

Make sure to check it, usually it is fine but sometimes mods have non-animal ThingDefs with identical generic labels that you might not want to remove.

It writes a file like this:
```xml
<?xml version="1.0" encoding="utf-8"?>
<Defs>
    <!-- Vanilla Animals Expanded > Animal Collab Project Vanilla-Style -->
    <CherryPicker.DefList MayRequire="owlchemist.cherrypicker, vanillaexpanded.vanillaanimalsexpanded, acpteam.acpvanillastyle">
        <defName>dupes_vanillaexpanded_vanillaanimalsexpanded_acpteam_acpvanillastyle</defName>
        <label>Vanilla Animals Expanded &gt; Animal Collab Project Vanilla-Style</label>
        <defs>
            <li MayRequire="vanillaexpanded.vanillaanimalsexpanded">PawnKindDef/ACPBlackbear</li> <!--AEXP_BlackBear/black bear-->
            <li MayRequire="vanillaexpanded.vanillaanimalsexpanded">PawnKindDef/ACPCheetah</li> <!--AEXP_Cheetah/cheetah-->
            <li MayRequire="vanillaexpanded.vanillaanimalsexpanded">PawnKindDef/ACPGiraffe</li> <!--AEXP_Giraffe/giraffe-->
            ... rest of duplicates ...
        </defs>
    </CherryPicker.DefList>
</Defs>
```
## Find all duplicates in your mods:
```py
rws.find_duplicates(r'D:\SteamLibrary\steamapps\workshop\content\294100)
```
It writes a file like this:
```xml
<?xml version="1.0" encoding="utf-8"?>
<Duplicates>
  <!-- exsanguinate -->
  <li>AbilityDef/Cexsanguinate</li> <!-- 1571323744/atomicravioli.crystalloid/`Crystalloid` -->
  <li>AbilityDef/HSAU_Ability_Exsanguinate</li> <!-- 2834801420/baskerville.hellsingarmsultimate/`Hellsing ARMS Ultimate` -->

  <!-- infernorocket -->
  <li>AbilityDef/LaunchInfernoRocket</li> <!-- 2968750452/blackmarket420.kraltechindustries/`Kraltech Industries` -->
  <li>AbilityDef/MooMF_BigInfernoRocket</li> <!-- 2819828894/mooloh.mythicitems/`Mooloh's Mythic Framework` -->

  <!-- ocularconversion -->
  <li>AbilityDef/AA_OcularConversion</li> <!-- 1541721856/sarg.alphaanimals/`Alpha Animals` -->
  <li>AbilityDef/AG_OcularConversionAlphaBiomes</li> <!-- 2891845502/sarg.alphagenes/`Alpha Genes` -->

  ... rest of duplicates ...
</Duplicates>
```
So filter using `types` argument to avoid junk like AbilityDefs

## Extract all defs from mods:
```py
rws.get_all_mod_defs([r'D:\SteamLibrary\steamapps\workshop\content\294100\2871933948', r'D:\SteamLibrary\steamapps\workshop\content\294100\2013243795'])
```
It writes a file like this (this one has types = 'FactionDef' attribute):
```xml
<?xml version="1.0" encoding="utf-8"?>
<AllDefs>
    <!-- Quartzian Race (Continued) / zal.quartzian / 2903484599 -->
    <li>FactionDef/QuartzFaction</li> <!-- Quartzian Grotto -->
    <li>FactionDef/QuartzPlayerColony</li> <!-- Quartzians -->

    <!-- Xenotype Pack - Exoplanet Adaptation / dpxp.exoadapt / 2902788054 -->
    <li>FactionDef/BehinderRoughVillage</li> <!-- the behinder resistance -->
    <li>FactionDef/ClimateWarlord</li> <!-- climate refugee warlords -->
    <li>FactionDef/DPXP_PlayerLeftBehind</li> <!-- The Left Behind -->
    <li>FactionDef/DusterHomesteads</li> <!-- duster homestead union -->\
  
    ... rest of all defs ...
</AllDefs>
```
## Search and count mods in gist.github logs with the same error as in your log:
```py
from RimWorld_Scrapper import log
log.find_sus_mods("[KCSG] Cannot add more symbolDef. Maximum amount reached")
```
this one prints:
```
TOP100 SUSPECTS:

98/98 HugsLib unlimitedhugs.hugslib
98/98 Vanilla Expanded Framework oskarpotocki.vanillafactionsexpanded.core
98/98 Core ludeon.rimworld
98/98 Harmony brrainz.harmony
88/98 Ideology ludeon.rimworld.ideology
86/98 Biotech ludeon.rimworld.biotech
86/98 Royalty ludeon.rimworld.royalty
... rest of the mods mentioned in logs...
```
Means HugsLib is in all 98 logs with your error, royalty is in 86 out of 98 logs
