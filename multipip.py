#########################################
# "multipip.py"                         #
#                                       #
# Download modules for multiple Python  #
# versions and OS distributions from    #
# the official PyPI website.            #
#########################################

__version__ = 1.0

# Imports
import requests
import shutil
import typer
from typing import List, Optional
from bs4 import BeautifulSoup
from pathlib import Path
from os.path import join, exists
from os import makedirs, getcwd
from sysconfig import get_platform


# Constants
BASE_URL = r"https://pypi.org/project/{}/#files"

class Whl_file:
    """ Parses name of .whl file """

    def __init__(self, name: str):
        self.full_name = name
        self.parse_name()

    def parse_name(self):
        split_name = self.full_name.rstrip(".whl").split("-")

        if len(split_name) == 5:
            (self.distribution, self.version,
            self.python_tag, self.abi_tag, self.platform_tag) = split_name
        else:
            (self.distribution, self.version, self.build_tag, 
            self.python_tag, self.abi_tag, self.platform_tag) = split_name


    def version_match(self, versions: List[str]):
        """
        Checks for python version match based on user 
        input and whl python_tag
        """
        if self.python_tag.endswith("py3"):
            return True
        elif (self.python_tag.startswith("cp3") and 
            # If name is in the format of cp3X(X) checks against asked versions
            f"3.{self.python_tag[3:]}" in versions):
            return True

        print(f"{self.python_tag} does not match any of the specified versions")
        return False

    def platform_match( self,
                        windows : bool = False,
                        linux : bool = False,
                        mac : bool = False  
                      ):
        """ Checks platform tag for match against list """
        if (("win" in self.platform_tag and windows) or 
            ("linux" in self.platform_tag and linux) or
            ("mac" in self.platform_tag and mac)):
            return True
        elif self.platform_tag == "any":
            return True
        
        print(f"{self.platform_tag} does not match any specified platform.")
        return False


# Credit to John Zwinck:
# https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
def fetch_file(url: str, save_dir : Path, file_name : str):
    
    with requests.get(url, stream=True) as resp:
        with open(join(save_dir, file_name), 'wb') as file:
            shutil.copyfileobj(resp.raw, file)
    return True

def main( 
    python_versions : List[str],
    module : str,
    dest : Optional[Path] = getcwd(),
    windows : bool = False,
    linux : bool = False,
    mac : bool = False
 ):

    # Creates dest dir if does'nt exist
    if not exists(dest):
        makedirs(dest, exist_ok=True)


    # # Downloads wheel files for all moduels specified
    # for module in modules:
        
    try:
        pypi_resp = requests.get(BASE_URL.format(module))
        pypi_resp.raise_for_status()
        soup = BeautifulSoup(pypi_resp.content, 'html.parser')
    except requests.RequestException as err:
        raise requests.RequestException(f"*** ERROR {err.__class__} ***\n{err} \n***")

    for element in soup.find_all("div", { "class" : "file" }):
        link = element.find("a")
        download_link = link.get('href')
        print(download_link)

        if not download_link.endswith(".whl"):
            continue

        file_name = Whl_file(download_link.split("/")[-1])

        if file_name.version_match(python_versions) and file_name.platform_match(windows, linux, mac):
            print("fetching")
            fetch_file(download_link, dest, file_name.full_name)
            # Verify



            

if __name__ == '__main__':
    typer.run(main)
