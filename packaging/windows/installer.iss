; SPDX-License-Identifier: GPL-3.0-or-later
; Instalador para Windows con Inno Setup 6 (https://jrsoftware.org/isinfo.php, libre).
; Lo ejecuta packaging\windows\build.ps1 después de PyInstaller. A mano:
;   ISCC.exe /DAppVersion=0.1.0 packaging\windows\installer.iss
; Resultado: dist\Quadrafall-<versión>-Windows-Setup.exe

#define AppName "Quadrafall"
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
#ifndef AppURL
  #define AppURL "https://github.com"
#endif

[Setup]
AppId={{6B1E8E5A-3C7D-4C1B-9F5E-7A2D9C4B8E10}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=Quadrafall contributors
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
AppUpdatesURL={#AppURL}/releases
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
LicenseFile=..\..\LICENSE
OutputDir=..\..\dist
OutputBaseFilename=Quadrafall-{#AppVersion}-Windows-Setup
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\Quadrafall.exe
UninstallDisplayName={#AppName}
; Se instala para el usuario actual, sin pedir permisos de administrador
; (en el asistente se puede elegir instalar para todos).
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ShowLanguageDialog=auto

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\..\dist\Quadrafall\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\Quadrafall.exe"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\Quadrafall.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Quadrafall.exe"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

; Los ajustes y récords del jugador (en %APPDATA%\Quadrafall) se conservan al desinstalar.
