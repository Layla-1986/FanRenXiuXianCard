#define MyAppName "凡人额度卡"
#define MyAppVersion "1.0.0"
#define MyAppExeName "MortalQuotaCard.exe"

[Setup]
AppId={{7B5099D9-991B-4BAA-918A-4B88629267E4}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Lelay
DefaultDirName={%LOCALAPPDATA}\Programs\MortalQuotaCard
DefaultGroupName={#MyAppName}
PrivilegesRequired=lowest
OutputDir=..\artifacts\installer
OutputBaseFilename=凡人额度卡-Setup-1.0.0
SetupIconFile=..\assets\mortal-quota-card.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
RestartApplications=no

[Files]
Source: "..\dist\MortalQuotaCard\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{userprograms}\{#MyAppName}"; Filename: "{%LOCALAPPDATA}\Programs\MortalQuotaCard\{#MyAppExeName}"; WorkingDir: "{%LOCALAPPDATA}\Programs\MortalQuotaCard"
Name: "{userprograms}\{#MyAppName}\卸载{#MyAppName}"; Filename: "{%LOCALAPPDATA}\Programs\MortalQuotaCard\unins000.exe"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{%LOCALAPPDATA}\Programs\MortalQuotaCard\{#MyAppExeName}"; WorkingDir: "{%LOCALAPPDATA}\Programs\MortalQuotaCard"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "启动{#MyAppName}"; Flags: nowait postinstall skipifsilent
