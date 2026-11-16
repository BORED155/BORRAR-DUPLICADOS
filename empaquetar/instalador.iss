; Instalador de Windows (Inno Setup). Lo compila el workflow windows.yml.
#ifndef Version
  #define Version "1.0.0"
#endif

[Setup]
AppId={{6B0E3C1D-5F2A-4C8E-9D17-B0A11D0F1E55}
AppName=Borrar duplicados
AppVersion={#Version}
AppPublisher=BORED155
DefaultDirName={localappdata}\Programs\Borrar duplicados
DefaultGroupName=Borrar duplicados
; Sin permisos de administrador: se instala solo para el usuario.
PrivilegesRequired=lowest
OutputDir=..\dist
OutputBaseFilename=BorrarDuplicados-instalador
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\BorrarDuplicados.exe

[Languages]
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "escritorio"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"

[Files]
Source: "..\dist\BorrarDuplicados\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\Borrar duplicados"; Filename: "{app}\BorrarDuplicados.exe"
Name: "{autodesktop}\Borrar duplicados"; Filename: "{app}\BorrarDuplicados.exe"; Tasks: escritorio

[Run]
Filename: "{app}\BorrarDuplicados.exe"; Description: "Abrir Borrar duplicados"; Flags: nowait postinstall skipifsilent
