from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.config import ConfigInteger, ConfigSelection, getConfigListEntry
from enigma import eTimer
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os
from datetime import datetime

PLUGIN_VERSION = "1.0"
PLUGIN_ICON = "icon.png"
PLUGIN_NAME = "CiefpSatellitesXmlEditor"
PLUGIN_DESCRIPTION = "Edit satellites.xml file"
# Putanja do satellites.xml
SATELLITES_XML_PATH = "/etc/tuxbox/satellites.xml"

# Dekodiranje vrednosti prema tabeli
POLARIZATION = {"0": "Horizontal", "1": "Vertical", "2": "Left", "3": "Right"}
FEC_INNER = {"0": "Auto", "1": "1/2", "2": "2/3", "3": "3/4", "4": "5/6", "5": "7/8", "6": "8/9", "7": "3/5", "8": "4/5", "9": "9/10"}
SYSTEM = {"0": "DVB-S", "1": "DVB-S2", "2": "None"}
MODULATION = {"0": "Auto", "1": "QPSK", "2": "8PSK", "3": "QAM16", "4": "16APSK", "5": "32APSK", "6": "None"}
PLS_MODE = {"0": "Root", "1": "Gold", "2": "Auto", "3": "Unknown"}

# Prvi ekran: Satellites.xml Reader
class CiefpSatelliteXmlReader(Screen):
    skin = """
    <screen name="CiefpSatelliteXmlReader" position="center,center" size="1800,800" title="..:: Ciefp Satellites.xml Reader ::..">
        <widget source="list" render="Listbox" position="0,0" size="1400,720" scrollbarMode="showOnDemand" itemHeight="30" font="Regular;24">
            <convert type="StringList" />
        </widget>
        <widget name="background" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CiefpSatelliteXmlEditor/background.png" position="1400,0" size="400,800" zPosition="-1" />
        <!-- Dugmići -->
        <ePixmap pixmap="/usr/share/enigma2/skin_default/buttons/red.png" position="100,750" size="40,40" alphatest="blend" />
        <ePixmap pixmap="/usr/share/enigma2/skin_default/buttons/green.png" position="350,750" size="40,40" alphatest="blend" />
        <ePixmap pixmap="/usr/share/enigma2/skin_default/buttons/yellow.png" position="600,750" size="40,40" alphatest="blend" />
        <ePixmap pixmap="/usr/share/enigma2/skin_default/buttons/blue.png" position="850,750" size="40,40" alphatest="blend" />
        <widget name="key_red" position="150,750" size="150,40" font="Regular;24" halign="left" valign="center" transparent="1" />
        <widget name="key_green" position="400,750" size="150,40" font="Regular;24" halign="left" valign="center" transparent="1" />
        <widget name="key_yellow" position="650,750" size="150,40" font="Regular;24" halign="left" valign="center" transparent="1" />
        <widget name="key_blue" position="900,750" size="150,40" font="Regular;24" halign="left" valign="center" transparent="1" />
    </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.list = []
        self["list"] = List(self.list)
        self["background"] = Pixmap()
        self["key_red"] = Label("Delete")
        self["key_green"] = Label("Save")
        self["key_yellow"] = Label("Edit")
        self["key_blue"] = Label("Add")
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions"], {
            "ok": self.okPressed,
            "cancel": self.close,
            "red": self.deleteLine,
            "green": self.saveChanges,
            "yellow": self.editLine,
            "blue": self.addLine
        }, -1)
        self.tree = None
        self.loadXml()

    def loadXml(self):
        try:
            self.tree = ET.parse(SATELLITES_XML_PATH)
            self.updateList()
        except Exception as e:
            self.session.open(MessageBox, f"Error loading satellites.xml: {str(e)}", MessageBox.TYPE_ERROR)

    def updateList(self):
        self.list = []
        root = self.tree.getroot()
        for sat in root.findall("sat"):
            sat_name = sat.get("name")
            sat_pos = sat.get("position")
            self.list.append((f"Satellite: {sat_name} ({sat_pos})", sat))
            for trans in sat.findall("transponder"):
                freq = int(trans.get("frequency", "0")) // 1000
                sr = int(trans.get("symbol_rate", "0")) // 1000
                pol = POLARIZATION.get(trans.get("polarization", "0"), "Unknown")
                fec = FEC_INNER.get(trans.get("fec_inner", "0"), "Unknown")
                sys = SYSTEM.get(trans.get("system", "0"), "Unknown")
                mod = MODULATION.get(trans.get("modulation", "0"), "Unknown")
                
                # Provera za multistream i T2-MI
                extra = []
                is_id = trans.get("is_id")
                pls_mode = trans.get("pls_mode")
                pls_code = trans.get("pls_code")
                t2mi_plp_id = trans.get("t2mi_plp_id")
                t2mi_pid = trans.get("t2mi_pid")
                
                if is_id and int(is_id) > 0:
                    extra.append(f"MIS: is_id={is_id}, pls_mode={PLS_MODE.get(pls_mode, 'Unknown')}, pls_code={pls_code}")
                if t2mi_plp_id and int(t2mi_plp_id) >= 0:
                    extra.append(f"T2-MI: plp_id={t2mi_plp_id}, pid={t2mi_pid or '0'}")
                
                display_text = f"  TR: {freq} {pol} {sr} {fec} {sys} {mod}"
                if extra:
                    display_text += f" [{' | '.join(extra)}]"
                
                self.list.append((display_text, trans))
        self["list"].setList(self.list)

    def okPressed(self):
        self.editLine()

    def deleteLine(self):
        cur = self["list"].getCurrent()
        if cur and isinstance(cur[1], ET.Element):
            root = self.tree.getroot()
            if cur[1].tag == "sat":
                # Ako je satelit, brišemo ga direktno iz root-a
                root.remove(cur[1])
            elif cur[1].tag == "transponder":
                # Ako je transponder, pronalazimo njegov satelit
                for sat in root.findall("sat"):
                    for trans in sat.findall("transponder"):
                        if trans == cur[1]:
                            sat.remove(trans)
                            break
                    else:
                        continue
                    break
            self.updateList()

    def saveChanges(self):
        try:
            # Generišemo XML string
            rough_string = ET.tostring(self.tree.getroot(), encoding='iso-8859-1')
            parsed = minidom.parseString(rough_string)
            pretty_xml = parsed.toprettyxml(indent="\t", encoding='iso-8859-1').decode('iso-8859-1')
            
            # Uklanjamo višak praznih redova
            lines = pretty_xml.split('\n')
            filtered_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('<?xml') and not stripped.startswith('<!'):
                    filtered_lines.append(line.rstrip())
                elif stripped.startswith('<?xml') or stripped.startswith('<!'):
                    filtered_lines.append(line)
            
            # Dodajemo prilagođeno zaglavlje
            current_date = datetime.now().strftime("%d.%m.%Y")
            header = f"""<?xml version="1.0" encoding="iso-8859-1"?>
<!--
\tFile edited by ciefp satellite.xml editor, {current_date}
-->
"""
            # Kombinujemo zaglavlje i filtrirani XML
            final_xml = header + '\n'.join(filtered_lines[1:])  # Preskačemo XML deklaraciju iz minidom-a

            # Upisujemo u fajl
            with open(SATELLITES_XML_PATH, 'w', encoding='iso-8859-1') as f:
                f.write(final_xml)
            
            self.session.open(MessageBox, "Changes saved successfully!", MessageBox.TYPE_INFO)
        except Exception as e:
            self.session.open(MessageBox, f"Error saving satellites.xml: {str(e)}", MessageBox.TYPE_ERROR)

    def editLine(self):
        cur = self["list"].getCurrent()
        if cur and isinstance(cur[1], ET.Element) and cur[1].tag == "transponder":
            self.session.open(CiefpSatelliteXmlEditor, cur[1], False)

    def addLine(self):
        cur = self["list"].getCurrent()
        if cur and isinstance(cur[1], ET.Element) and cur[1].tag == "sat":
            self.session.open(CiefpSatelliteXmlEditor, cur[1], True)

# Drugi ekran: Satellites.xml Editor
class CiefpSatelliteXmlEditor(ConfigListScreen, Screen):
    skin = """
    <screen name="CiefpSatelliteXmlEditor" position="center,center" size="1600,800" title="..:: Ciefp Satellites.xml Editor ::..">
        <widget name="config" position="0,0" size="1000,720" scrollbarMode="showOnDemand" itemHeight="36" font="Regular;26" />
        <widget name="background" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/CiefpSatelliteXmlEditor/background2.png" position="1000,0" size="600,800" zPosition="-1" />
        <!-- Dugmići -->
        <ePixmap pixmap="/usr/share/enigma2/skin_default/buttons/green.png" position="350,750" size="40,40" alphatest="blend" />
        <ePixmap pixmap="/usr/share/enigma2/skin_default/buttons/yellow.png" position="650,750" size="40,40" alphatest="blend" />
        <widget name="key_green" position="400,750" size="200,40" font="Regular;24" halign="left" valign="center" transparent="1" />
        <widget name="key_yellow" position="700,750" size="200,40" font="Regular;24" halign="left" valign="center" transparent="1" />
    </screen>"""

    def __init__(self, session, element, is_new):
        Screen.__init__(self, session)
        ConfigListScreen.__init__(self, [])
        self.session = session
        self.element = element
        self.is_new = is_new
        self["background"] = Pixmap()
        self["key_green"] = Label("Save")
        self["key_yellow"] = Label("Edit")
        self.createConfig()
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions"], {
            "ok": self.okPressed,
            "cancel": self.close,
            "green": self.save,
            "yellow": self.edit
        }, -1)

    def createConfig(self):
        self.config_list = []
        if self.is_new:
            self.frequency = ConfigInteger(default=0, limits=(0, 99999))
            self.symbol_rate = ConfigInteger(default=0, limits=(0, 99999))
            self.polarization = ConfigSelection(choices=POLARIZATION, default="0")
            self.fec_inner = ConfigSelection(choices=FEC_INNER, default="0")
            self.system = ConfigSelection(choices=SYSTEM, default="0")
            self.modulation = ConfigSelection(choices=MODULATION, default="0")
            self.is_id = ConfigInteger(default=0, limits=(0, 255))
            self.pls_code = ConfigInteger(default=0, limits=(0, 262141))
            self.pls_mode = ConfigSelection(choices=PLS_MODE, default="2")
            self.t2mi_plp_id = ConfigInteger(default=-1, limits=(-1, 255))
            self.t2mi_pid = ConfigInteger(default=0, limits=(0, 8192))
        else:
            self.frequency = ConfigInteger(default=int(self.element.get("frequency", "0")) // 1000, limits=(0, 99999))
            self.symbol_rate = ConfigInteger(default=int(self.element.get("symbol_rate", "0")) // 1000, limits=(0, 99999))
            self.polarization = ConfigSelection(choices=POLARIZATION, default=self.element.get("polarization", "0"))
            self.fec_inner = ConfigSelection(choices=FEC_INNER, default=self.element.get("fec_inner", "0"))
            self.system = ConfigSelection(choices=SYSTEM, default=self.element.get("system", "0"))
            self.modulation = ConfigSelection(choices=MODULATION, default=self.element.get("modulation", "0"))
            self.is_id = ConfigInteger(default=int(self.element.get("is_id", "0")), limits=(0, 255))
            self.pls_code = ConfigInteger(default=int(self.element.get("pls_code", "0")), limits=(0, 262141))
            self.pls_mode = ConfigSelection(choices=PLS_MODE, default=self.element.get("pls_mode", "2"))
            self.t2mi_plp_id = ConfigInteger(default=int(self.element.get("t2mi_plp_id", "-1")), limits=(-1, 255))
            self.t2mi_pid = ConfigInteger(default=int(self.element.get("t2mi_pid", "0")), limits=(0, 8192))

        self.config_list.append(getConfigListEntry("Frequency (MHz)", self.frequency))
        self.config_list.append(getConfigListEntry("Symbol Rate (kS/s)", self.symbol_rate))
        self.config_list.append(getConfigListEntry("Polarization", self.polarization))
        self.config_list.append(getConfigListEntry("FEC", self.fec_inner))
        self.config_list.append(getConfigListEntry("System", self.system))
        self.config_list.append(getConfigListEntry("Modulation", self.modulation))
        self.config_list.append(getConfigListEntry("Multistream ID (0=off)", self.is_id))
        self.config_list.append(getConfigListEntry("PLS Code", self.pls_code))
        self.config_list.append(getConfigListEntry("PLS Mode", self.pls_mode))
        self.config_list.append(getConfigListEntry("T2-MI PLP ID (-1=off)", self.t2mi_plp_id))
        self.config_list.append(getConfigListEntry("T2-MI PID", self.t2mi_pid))
        self["config"].list = self.config_list

    def okPressed(self):
        self.edit()

    def edit(self):
        self.keyRight()

    def save(self):
        if self.is_new:
            new_trans = ET.SubElement(self.element, "transponder")
            self.element = new_trans
        self.element.set("frequency", str(self.frequency.value * 1000))
        self.element.set("symbol_rate", str(self.symbol_rate.value * 1000))
        self.element.set("polarization", self.polarization.value)
        self.element.set("fec_inner", self.fec_inner.value)
        self.element.set("system", self.system.value)
        self.element.set("modulation", self.modulation.value)
        
        # Upisujemo multistream parametre samo ako je is_id > 0
        if self.is_id.value > 0:
            self.element.set("is_id", str(self.is_id.value))
            self.element.set("pls_code", str(self.pls_code.value))
            self.element.set("pls_mode", self.pls_mode.value)
        else:
            # Uklanjamo ako postoje
            for attr in ["is_id", "pls_code", "pls_mode"]:
                if attr in self.element.attrib:
                    del self.element.attrib[attr]
        
        # Upisujemo T2-MI parametre samo ako je t2mi_plp_id >= 0
        if self.t2mi_plp_id.value >= 0:
            self.element.set("t2mi_plp_id", str(self.t2mi_plp_id.value))
            self.element.set("t2mi_pid", str(self.t2mi_pid.value))
        else:
            # Uklanjamo ako postoje
            for attr in ["t2mi_plp_id", "t2mi_pid"]:
                if attr in self.element.attrib:
                    del self.element.attrib[attr]
        
        self.close()

# Plugin descriptor
def main(session, **kwargs):
    session.open(CiefpSatelliteXmlReader)

def Plugins(**kwargs):
    return PluginDescriptor(
        name="{0} v{1}".format(PLUGIN_NAME, PLUGIN_VERSION),
        description="Edit satellites.xml file",
        icon=PLUGIN_ICON,
        where=PluginDescriptor.WHERE_PLUGINMENU,
        fnc=main
    )