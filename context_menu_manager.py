import sys
import ctypes
import winreg
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QListWidget, QComboBox, QListWidgetItem, QSizePolicy, QSpacerItem, QTextEdit
)
from PyQt6.QtCore import Qt

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

CONTEXT_MENU_LOCATIONS = {
    "Dosya (File)": r"*\shell",
    "Klasör (Folder)": r"Directory\shell",
    "Masaüstü (Desktop)": r"DesktopBackground\shell"
}

ROOT_KEYS = {
    "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
    "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
    "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
}

APPROVED_CLSID_PATHS = [
    r"Software\Microsoft\Windows\CurrentVersion\Shell Extensions\Approved",
    r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Shell Extensions\Approved"
]

def enum_subkeys(root, path):
    keys = []
    for wow_flag in [winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY]:
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_READ | wow_flag) as key:
                i = 0
                while True:
                    try:
                        subkey = winreg.EnumKey(key, i)
                        if subkey not in keys:
                            keys.append(subkey)
                        i += 1
                    except OSError as e:
                        if e.winerror == 259:  # no more data
                            break
                        else:
                            raise
        except FileNotFoundError:
            continue
    return keys

def get_clsid_description(clsid):
    for root in [winreg.HKEY_CLASSES_ROOT, winreg.HKEY_LOCAL_MACHINE]:
        try:
            with winreg.OpenKey(root, r"CLSID\\" + clsid) as key:
                desc, _ = winreg.QueryValueEx(key, None)
                if desc:
                    return desc
        except:
            continue
    for root_name in ["HKEY_LOCAL_MACHINE", "HKEY_CURRENT_USER"]:
        root = ROOT_KEYS.get(root_name)
        for approved_path in APPROVED_CLSID_PATHS:
            try:
                with winreg.OpenKey(root, approved_path) as key:
                    i = 0
                    while True:
                        try:
                            name = winreg.EnumValue(key, i)[0]
                            val = winreg.EnumValue(key, i)[1]
                            if val.upper() == clsid.upper():
                                return name
                            i += 1
                        except OSError:
                            break
            except:
                continue
    return clsid

def get_com_clsid_info(clsid):
    clsid = clsid.strip("{}").upper()
    base_path = fr"CLSID\{{{clsid}}}"
    info = {}
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, base_path) as key:
            desc, _ = winreg.QueryValueEx(key, None)
            info["Description"] = desc

            try:
                with winreg.OpenKey(key, "InprocServer32") as subkey:
                    dll_path, _ = winreg.QueryValueEx(subkey, None)
                    info["InprocServer32"] = dll_path
            except FileNotFoundError:
                info["InprocServer32"] = None

            try:
                with winreg.OpenKey(key, "LocalServer32") as subkey:
                    exe_path, _ = winreg.QueryValueEx(subkey, None)
                    info["LocalServer32"] = exe_path
            except FileNotFoundError:
                info["LocalServer32"] = None

            try:
                progid, _ = winreg.QueryValueEx(key, "ProgID")
                info["ProgID"] = progid
            except FileNotFoundError:
                info["ProgID"] = None

            try:
                typelib, _ = winreg.QueryValueEx(key, "TypeLib")
                info["TypeLib"] = typelib
            except FileNotFoundError:
                info["TypeLib"] = None

            props = {}
            try:
                with winreg.OpenKey(key, "Properties") as props_key:
                    i = 0
                    while True:
                        try:
                            val_name, val_data, _ = winreg.EnumValue(props_key, i)
                            props[val_name] = val_data
                            i += 1
                        except OSError:
                            break
                info["Properties"] = props
            except FileNotFoundError:
                info["Properties"] = {}

        return info
    except Exception as e:
        return {"Error": str(e)}

class ContextMenuManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sağ Tık Menüsü Düzenleyici (Detaylı CLSID Analizi + Filtre)")
        self.setMinimumSize(1200, 700)
        self.current_clsid_info = None
        self.init_ui()
        self.load_context_menu_items()

    def init_ui(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout, 4)

        left_layout.addWidget(QLabel("Menü Konumu Seçin:"))
        self.cmb_location = QComboBox()
        self.cmb_location.addItems(CONTEXT_MENU_LOCATIONS.keys())
        left_layout.addWidget(self.cmb_location)

        left_layout.addWidget(QLabel("Mevcut Menü Öğeleri:"))
        self.lst_items = QListWidget()
        left_layout.addWidget(self.lst_items)

        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout, 6)

        right_layout.addWidget(QLabel("Menüde Görünecek İsim:"))
        self.txt_name = QLineEdit()
        right_layout.addWidget(self.txt_name)

        right_layout.addWidget(QLabel("Çalıştırılacak Komut (Yol):"))
        self.txt_command = QLineEdit()
        right_layout.addWidget(self.txt_command)

        right_layout.addWidget(QLabel("CLSID Detayları Filtre:"))
        self.txt_filter = QLineEdit()
        self.txt_filter.setPlaceholderText("Filtrelemek için yazınız...")
        right_layout.addWidget(self.txt_filter)

        right_layout.addWidget(QLabel("CLSID Detayları:"))
        self.txt_clsid_details = QTextEdit()
        self.txt_clsid_details.setReadOnly(True)
        self.txt_clsid_details.setStyleSheet("background-color: #252526; color: #e0e0e0; font-family: Consolas, monospace;")
        right_layout.addWidget(self.txt_clsid_details)

        btn_layout = QHBoxLayout()
        right_layout.addLayout(btn_layout)

        self.btn_add_update = QPushButton("Ekle / Güncelle")
        self.btn_add_update.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        btn_layout.addWidget(self.btn_add_update)

        self.btn_remove = QPushButton("Sil")
        self.btn_remove.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        btn_layout.addWidget(self.btn_remove)

        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        right_layout.addItem(spacer)

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 14px;
            }
            QLineEdit, QComboBox, QListWidget, QTextEdit {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                padding: 5px;
                color: #e0e0e0;
            }
            QPushButton {
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                opacity: 0.85;
            }
            QListWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
        """)

        self.cmb_location.currentIndexChanged.connect(self.load_context_menu_items)
        self.lst_items.itemClicked.connect(self.load_item_to_fields)
        self.btn_add_update.clicked.connect(self.add_or_update_item)
        self.btn_remove.clicked.connect(self.remove_item)
        self.txt_filter.textChanged.connect(self.filter_clsid_details)

    def get_registry_paths_for_location(self, root_name):
        base = CONTEXT_MENU_LOCATIONS[self.cmb_location.currentText()]

        shell_paths = []
        shellex_paths = []

        if root_name == "HKEY_CLASSES_ROOT":
            shell_paths = [base]
            shellex_paths = [base.replace(r"\shell", r"\shellex\ContextMenuHandlers")]
        else:
            shell_paths = [r"Software\Classes\\" + base]
            shellex_paths = [r"Software\Classes\\" + base.replace(r"\shell", r"\shellex\ContextMenuHandlers")]

            shell_paths.append(r"Software\Wow6432Node\Classes\\" + base)
            shellex_paths.append(r"Software\Wow6432Node\Classes\\" + base.replace(r"\shell", r"\shellex\ContextMenuHandlers"))

        return shell_paths, shellex_paths

    def load_context_menu_items(self):
        self.lst_items.clear()

        items = []

        for root_name, root in ROOT_KEYS.items():
            shell_paths, shellex_paths = self.get_registry_paths_for_location(root_name)

            for spath in shell_paths:
                subs = enum_subkeys(root, spath)
                for sub in subs:
                    display = f"{root_name} Shell | {spath}\\{sub}"
                    items.append((display, root_name, spath, sub, "shell", None))

            for spath in shellex_paths:
                subs = enum_subkeys(root, spath)
                for sub in subs:
                    clsid = None
                    try:
                        with winreg.OpenKey(root, spath + "\\" + sub) as skey:
                            clsid, _ = winreg.QueryValueEx(skey, None)
                    except Exception:
                        pass

                    clsid_info = None
                    desc = sub

                    if clsid and clsid.startswith("{") and clsid.endswith("}"):
                        clsid_desc = get_clsid_description(clsid)
                        clsid_info = get_com_clsid_info(clsid)

                        extra_info = []
                        if clsid_desc:
                            extra_info.append(f"Açıklama: {clsid_desc}")
                        if clsid_info.get("InprocServer32"):
                            extra_info.append(f'DLL: {clsid_info["InprocServer32"]}')
                        if clsid_info.get("LocalServer32"):
                            extra_info.append(f'EXE: {clsid_info["LocalServer32"]}')
                        if clsid_info.get("ProgID"):
                            extra_info.append(f'ProgID: {clsid_info["ProgID"]}')
                        if clsid_info.get("TypeLib"):
                            extra_info.append(f'TypeLib: {clsid_info["TypeLib"]}')
                        if clsid_info.get("Properties"):
                            props_str = ", ".join(f"{k}={v}" for k,v in clsid_info["Properties"].items())
                            extra_info.append(f'Properties: {props_str}')

                        desc = f'{sub} => ' + "; ".join(extra_info)

                    else:
                        desc = f'{sub} => {sub}'

                    display = f"{root_name} CMH | {spath}\\{sub} => {desc}"
                    items.append((display, root_name, spath, sub, "cmh", clsid_info))

        seen = set()
        for text, root_name, path, subkey, tp, clsid_info in items:
            if text not in seen:
                self.lst_items.addItem(text)
                seen.add(text)

        self.txt_name.clear()
        self.txt_command.clear()
        self.txt_clsid_details.clear()
        self.current_clsid_info = None
        self.txt_filter.clear()

    def load_item_to_fields(self, item: QListWidgetItem):
        text = item.text()
        try:
            parts = text.split('|')
            root_part = parts[0].strip()
            path_part = parts[1].strip()

            if root_part.endswith("Shell"):
                root_name = root_part.split()[0]
                root = ROOT_KEYS[root_name]
                base_path, subkey_name = path_part.rsplit('\\', 1)
                command_key_path = f"{base_path}\\{subkey_name}\\command"
            elif root_part.endswith("CMH"):
                root_name = root_part.split()[0]
                root = ROOT_KEYS[root_name]
                base_path, subkey_name = path_part.split("=>")[0].strip().rsplit('\\', 1)
                command_key_path = None
            else:
                root = None
                command_key_path = None

            if "=>" in path_part:
                name = path_part.split("=>")[1].strip()
                self.txt_name.setText(name)
            else:
                self.txt_name.setText(subkey_name)

            if command_key_path:
                try:
                    with winreg.OpenKey(root, command_key_path) as cmd_key:
                        command, _ = winreg.QueryValueEx(cmd_key, None)
                        self.txt_command.setText(command)
                except FileNotFoundError:
                    self.txt_command.setText("")
                except Exception as e:
                    QMessageBox.warning(self, "Hata", f"Komut yüklenirken hata: {e}")
                    self.txt_command.setText("")
            else:
                self.txt_command.setText("")

            if root_part.endswith("CMH"):
                try:
                    with winreg.OpenKey(root, base_path + "\\" + subkey_name) as key:
                        clsid, _ = winreg.QueryValueEx(key, None)
                        info = get_com_clsid_info(clsid)
                        self.current_clsid_info = info
                        self.apply_filter_and_show()
                except Exception as e:
                    self.txt_clsid_details.setPlainText(f"CLSID detayları okunamadı:\n{e}")
                    self.current_clsid_info = None
            else:
                self.txt_clsid_details.clear()
                self.current_clsid_info = None

        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Öğe detayları yüklenirken hata: {e}")
            self.current_clsid_info = None

    def apply_filter_and_show(self):
        if not self.current_clsid_info:
            self.txt_clsid_details.clear()
            return

        filter_text = self.txt_filter.text().lower()
        lines = []

        for k, v in self.current_clsid_info.items():
            if k != "Properties":
                line = f"{k}: {v}"
                if filter_text in line.lower():
                    lines.append(line)

        if "Properties" in self.current_clsid_info and self.current_clsid_info["Properties"]:
            prop_lines = []
            for pk, pv in self.current_clsid_info["Properties"].items():
                prop_line = f"  {pk} = {pv}"
                if filter_text in prop_line.lower():
                    prop_lines.append(prop_line)
            if prop_lines:
                if filter_text in "properties":
                    lines.append("Properties:")
                lines.extend(prop_lines)

        self.txt_clsid_details.setPlainText("\n".join(lines))

    def filter_clsid_details(self):
        self.apply_filter_and_show()

    def add_or_update_item(self):
        name = self.txt_name.text().strip()
        command = self.txt_command.text().strip()
        if not name or not command:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun.")
            return

        base_path = self.get_registry_path()
        key_path = base_path + f"\\" + name
        command_path = key_path + r"\command"

        try:
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path) as key:
                winreg.SetValueEx(key, None, 0, winreg.REG_SZ, name)
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, command_path) as cmd_key:
                winreg.SetValueEx(cmd_key, None, 0, winreg.REG_SZ, command)
            QMessageBox.information(self, "Başarılı", f"'{name}' menüye eklendi/güncellendi.")
            self.load_context_menu_items()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu:\n{e}")

    def remove_item(self):
        name = self.txt_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Hata", "Lütfen silinecek menü öğesini seçin.")
            return
        base_path = self.get_registry_path()
        key_path = base_path + f"\\" + name
        command_path = key_path + r"\command"

        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, command_path)
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, key_path)
            QMessageBox.information(self, "Başarılı", f"'{name}' menüden kaldırıldı.")
            self.load_context_menu_items()
            self.txt_name.clear()
            self.txt_command.clear()
            self.txt_clsid_details.clear()
            self.current_clsid_info = None
            self.txt_filter.clear()
        except FileNotFoundError:
            QMessageBox.warning(self, "Uyarı", f"'{name}' adlı menü öğesi bulunamadı.")
        except OSError as e:
            if e.winerror == 145:
                QMessageBox.warning(self, "Hata", f"Menü öğesi silinemedi, alt anahtarlar var.")
            else:
                QMessageBox.critical(self, "Hata", f"Bir hata oluştu:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu:\n{e}")

    def get_registry_path(self):
        selected_location = self.cmb_location.currentText()
        return CONTEXT_MENU_LOCATIONS[selected_location]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ContextMenuManager()
    window.show()
    sys.exit(app.exec())
