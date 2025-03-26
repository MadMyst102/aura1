# PyInstaller hook for cryptography module
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect all submodules
hiddenimports = collect_submodules('cryptography')

# Explicitly add _cffi_backend which is required by cryptography
hiddenimports.append('_cffi_backend')

# Collect all data files and binaries
# collect_all returns a tuple of (datas, binaries, hiddenimports)
datas, binaries, additional_imports = collect_all('cryptography')
# Extend our hiddenimports with the ones from collect_all
hiddenimports.extend(additional_imports)