import variables as var
import functions as fn
import os
import shutil
import ctypes
import sys

def run():
    try:
        legacy_check = False
        if not os.path.exists(var.settings['path']):
            os.mkdir(var.settings['path'])
            var.status['first'] = True
        else:
            var.status['first'] = False
            for item in os.listdir(var.settings['path']):
                var.status['first'] = True
                legacy_check = True # If the I5G Tools folder already existed, but no subfolders exist, assume v0.4.4b
                if not legacy_check or os.path.isdir(os.path.join(var.settings['path'], item)): # if subfolders exist, assume not v0.4.4b
                    var.status['first'] = False
                    legacy_check = False

        if legacy_check:
            text = "Do you want to upgrade from v0.4.4b to " + var.lang['version'] + "?\n\n"
            text+= "Press OK to upgrade. Note: the app will load the first time with a blank default profile, but you can select any other profiles you already had saved.\n\n"
            text+= "Press Cancel if you do not wish to upgrade, or if you are NOT upgrading from v0.4.4b."
            response = ctypes.windll.user32.MessageBoxW(0, text, "I5G Tools  -  Upgrade from v0.4.4b to " + var.lang['version'] + "?", 1)
            if response == 1:
                pass
            elif response == 2:
                sys.exit(0)

        for sub_setting in var.settings:
            if isinstance(var.settings[sub_setting], dict) and 'path' in var.settings[sub_setting]:
                if not os.path.exists(var.settings['path'] + "\\" + var.settings[sub_setting]['path']):
                    os.mkdir(var.settings['path'] + "\\" + var.settings[sub_setting]['path'])
        
        if legacy_check:
            source_dir = var.settings['path']
            target_dir = var.settings['path'] + "\\" + "profiles"
            file_names = os.listdir(source_dir)
            for file in file_names:
                root, extension = os.path.splitext(file)
                if extension.lower() == ".ini" and not file == "global.ini":
                    source_path = os.path.join(source_dir, file)
                    target_path = os.path.join(target_dir, file)

                    try:
                        shutil.move(source_path, target_path)
                    except Exception as e:
                        print("Error moving file {file}: {e}")
    except Exception as e:
        fn.error_handling(e, "check_dir.run()")