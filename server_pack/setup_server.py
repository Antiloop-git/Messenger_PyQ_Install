import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["common", "logs", "server", "unit_tests"],
}
setup(
    name="server_PyQ",
    version="1.0.0",
    description="server_PyQ files",
    options={
        "build_exe": build_exe_options
    },
    executables=[Executable('server.py',
                            # base='Win32GUI',
                            targetName='server.exe',
                            )]
)
