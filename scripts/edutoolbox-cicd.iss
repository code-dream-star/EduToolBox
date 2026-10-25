#define CW_VERSION "{#CW_VERSION}"

[Setup]
AppName=EduToolBox
AppVersion={#CW_VERSION}
DefaultDirName={autopf}\EduToolBox
DefaultGroupName=EduToolBox
OutputDir=output
OutputBaseFilename=EduToolBox-{#CW_VERSION}-Win-Installer
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
UninstallDisplayIcon={app}\EduToolBox.exe

[Files]
Source: "..\dist\EduToolBox\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{autodesktop}\EduToolBox"; Filename: "{app}\EduToolBox.exe"
Name: "{group}\EduToolBox"; Filename: "{app}\EduToolBox.exe"
Name: "{group}\卸载 EduToolBox"; Filename: "{uninstallexe}"
