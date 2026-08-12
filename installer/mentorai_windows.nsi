; MentorAI - Instalador Windows x64
; Este instalador solo debe ejecutarse después de generar dist\MentorAI.exe

Unicode True
Name "MentorAI"
OutFile "..\dist\MentorAI-Setup.exe"
InstallDir "$PROGRAMFILES64\MentorAI"
InstallDirRegKey HKLM "Software\MentorAI" "InstallDir"
RequestExecutionLevel admin
SetCompressor /SOLID lzma

VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "MentorAI"
VIAddVersionKey "CompanyName" "MentorAI Project"
VIAddVersionKey "FileDescription" "Asistente educativo local"
VIAddVersionKey "FileVersion" "1.0.0"
VIAddVersionKey "LegalCopyright" "Copyright (c) MentorAI Project"

Page directory
Page instfiles
UninstPage uninstConfirm
UninstPage instfiles

Section "MentorAI" SEC_MAIN
  SetOutPath "$INSTDIR"
  File "..\dist\MentorAI.exe"
  File "..\README.md"

  CreateDirectory "$APPDATA\MentorAI"
  CreateDirectory "$SMPROGRAMS\MentorAI"
  CreateShortCut "$SMPROGRAMS\MentorAI\MentorAI.lnk" "$INSTDIR\MentorAI.exe"
  CreateShortCut "$DESKTOP\MentorAI.lnk" "$INSTDIR\MentorAI.exe"

  WriteUninstaller "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\MentorAI" "InstallDir" "$INSTDIR"
  WriteRegStr HKLM "Software\MentorAI" "Version" "1.0.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MentorAI" "DisplayName" "MentorAI"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MentorAI" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MentorAI" "DisplayVersion" "1.0.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MentorAI" "Publisher" "MentorAI Project"
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\MentorAI.lnk"
  Delete "$SMPROGRAMS\MentorAI\MentorAI.lnk"
  RMDir "$SMPROGRAMS\MentorAI"
  Delete "$INSTDIR\MentorAI.exe"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
  DeleteRegKey HKLM "Software\MentorAI"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MentorAI"
SectionEnd
