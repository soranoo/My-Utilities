import subprocess
import sys
import os
import time

def try_import(import_module:str, submodules:list=[], pip_package_name:str=None):
    """
    Try import the given module, return the module if success
    else install the module when the user confirm(said yes)
    return the module after installation

    Args:
        import_module (str): Module to import
        submodules (list[str], optional): Submodules to import. Defaults to [None].
        pip_package_name (str, optional): The name of the package in PyPI. Defaults to None.

    Example:
        [1. import check and import]
        FROM:  from discord.embeds import Embed OtherModule
        TO:    Embed = try_import("discord.embeds", ["Embed", "OtherModule"], "discord.py").Embed
        
        [2. just do the import check]
        FROM: from discord.embeds import Embed
        TO:    try_import("discord", pip_package_name="discord.py")
               from discord.embeds import Embed

    Returns:
        module: The module
    """
    try:
        module = __import__(import_module, fromlist=submodules)
        return module
    except ModuleNotFoundError:
        if pip_package_name is None:
            pip_package_name = import_module
        print(f"Module '{import_module}' not found.")
        print("Do you want to install this module? (y/n)")
        if input().lower() == "y":
            print("Installing module...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_package_name])
            print("Module installed.")
            time.sleep(1)
            os.system("cls")
            return __import__(import_module, fromlist=submodules)
        else:
            exit()