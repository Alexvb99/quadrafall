; SPDX-License-Identifier: GPL-3.0-or-later
; Instalador para Windows con Inno Setup (https://jrsoftware.org/isinfo.php, libre).
; Primero ejecuta packaging\windows\build.ps1 y luego compila este archivo con ISCC.exe.

#define AppName "Quadrafall"
#define AppVersion "0.1.0"

[Setup]
AppId={{6B1E8E5A-3C7D-4C1B-9F5E-7A2D9C4B8E10}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Quadrafall contributors
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
LicenseFile=..\..\LICENSE
OutputDir=..\..\dist
OutputBaseFilename=Quadrafall-{#AppVersion}-setup
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\Quadrafall.exe
Compression=lzma2
SolidCompression=yes
PrivilegesRequiredOverridesAllowed=dialog
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\..\dist\Quadrafall\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\Quadrafall.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\Quadrafall.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Quadrafall.exe"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
