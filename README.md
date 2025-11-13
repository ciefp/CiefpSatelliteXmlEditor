
# CiefpSatellitesXmlEditor

![Enigma2](https://img.shields.io/badge/Enigma2-Plugin-blue)
![Python](https://img.shields.io/badge/Python-2.7%2B%20%7C%203.x-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![DVB-S/S2](https://img.shields.io/badge/DVB--S%2FS2-Editor-success)
![XML](https://img.shields.io/badge/XML-Editor-orange)

> **Advanced satellites.xml editor with live tuner detection and transponder management**

`CiefpSatellitesXmlEditor` is a powerful Enigma2 plugin that allows **direct editing of `satellites.xml`** with real-time tuner feedback. Perfect for advanced users, installers, and satellite enthusiasts who need to fine-tune or repair transponder lists.

---

## Features

- **Live tuner integration** – highlights currently tuned transponder
- **Add, edit, delete** satellites and transponders
- **Smart sorting** – new transponders inserted by frequency
- **Full MIS (Multistream) support**:
  - `is_id`, `pls_mode`, `pls_code`
- **T2-MI support**:
  - `t2mi_plp_id`, `t2mi_pid`
- **Pretty XML output** with header and date
- **Dual save** to `/etc/tuxbox/satellites.xml` **and** `/etc/enigma2/satellites.xml`
- **Clean & intuitive GUI** with color buttons

---

## Screenshots

| ![Main](https://github.com/ciefp/CiefpSatelliteXmlEditor/blob/main/screenshot1.jpg) |
| ![Editor](https://github.com/ciefp/CiefpSatelliteXmlEditor/blob/main/screenshot2.jpg) |

---

## Requirements

| Requirement | Description |
|------------|-----------|
| **Enigma2 image** | OpenPLi, OpenATV, VTi, BlackHole, etc. |
| **Root access** | Write permissions to `/etc/tuxbox/` and `/etc/enigma2/` |
| **DVB-S/S2 tuner** | Optional (for live detection) |
| **Python** | 2.7+ (included in Enigma2) |

> No external packages required.

---

## Installation

### 1. Download Plugin

```bash
wget https://github.com/ciefp/CiefpSatellitesXmlEditor/archive/refs/heads/main.zip
unzip main.zip
```

### 2. Copy to Device

```bash
scp -r CiefpSatellitesXmlEditor-main/usr/lib/enigma2/python/Plugins/Extensions/CiefpSatellitesXmlEditor root@your-box-ip:/usr/lib/enigma2/python/Plugins/Extensions/
```

### 3. Copy Assets (Optional)

```bash
scp CiefpSatellitesXmlEditor-main/usr/lib/enigma2/python/Plugins/Extensions/CiefpSatellitesXmlEditor/*.png root@your-box-ip:/usr/lib/enigma2/python/Plugins/Extensions/CiefpSatellitesXmlEditor/
```

### 4. Restart Enigma2

```bash
init 4 && sleep 2 && init 3
```

> Plugin appears in **Extensions Menu**

---

## Usage

| Button | Action |
|-------|--------|
| **Red** | Delete selected satellite or transponder |
| **Green** | Save changes to both `satellites.xml` files |
| **Yellow** | Edit selected transponder |
| **Blue** | Add new transponder to selected satellite |
| **OK** | Edit transponder |

### Live Tuner Highlight
- Tune to any channel
- Open plugin → currently tuned **transponder is auto-selected**
- Great for verifying or fixing broken entries

---

## File Locations

| Path | Purpose |
|------|--------|
| `/etc/tuxbox/satellites.xml` | Main rotor/USALS config |
| `/etc/enigma2/satellites.xml` | Enigma2 fallback (auto-synced) |
| `/usr/lib/enigma2/python/Plugins/Extensions/CiefpSatellitesXmlEditor/` | Plugin files |

---

## Configuration

No config file needed.  
Plugin reads and writes directly to `satellites.xml`.

> **Backup before editing!**
```bash
cp /etc/tuxbox/satellites.xml /etc/tuxbox/satellites.xml.bak
```

---

## Troubleshooting

| Issue | Solution |
|------|----------|
| Plugin not visible | Check path and restart GUI |
| Permission denied | Use `root` via Telnet/FTP |
| XML corrupted | Restore from backup |
| No live highlight | Tune to DVB-S channel first |
| T2-MI not working | Set `t2mi_plp_id ≥ 0` |

---

## Contributing

We welcome contributions!

1. Fork the repo
2. Create branch: `git checkout -b feature/mis-enhancement`
3. Commit changes
4. Open **Pull Request**

**Ideas**:
- Auto-backup on save
- Import from `lamedb`
- Search & filter
- Dark mode skin

---

## Author

- **ciefp** – [GitHub Profile](https://github.com/ciefp)
- Report bugs: [Open Issue](https://github.com/ciefp/CiefpSatellitesXmlEditor/issues)

---

## License

```plaintext
MIT License © 2025 ciefp
```

> Free to use, modify, and distribute.

---

## Star the Project

Love the plugin? Star it on GitHub!

[![GitHub stars](https://img.shields.io/github/stars/ciefp/CiefpSatellitesXmlEditor?style=social)](https://github.com/ciefp/CiefpSatellitesXmlEditor)

---

> **Warning**: Always backup `satellites.xml` before editing. Incorrect values may break rotor control.

---

### Next Steps (Optional)

Add these files to your repo:
- `LICENSE` (MIT)
- `docs/screenshots/main.png`, `editor.png`
- `icon.png`, `background.png`, `background2.png`
- `CHANGELOG.md`

**Want me to generate any of these?** Just ask!
```
