; MentorAI - Instalador NSIS Simplificado

!include "MUI2.nsh"

Name "MentorAI v1.0.0"
OutFile "..\dist\MentorAI-Installer.exe"
InstallDir "$PROGRAMFILES\MentorAI"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "Spanish"

Section "Instalar MentorAI"
  SetOutPath "$INSTDIR"
  File "..\dist\MentorAI-Windows"
  File "..\README.md"
  
  CreateDirectory "$SMPROGRAMS\MentorAI"
  CreateShortCut "$SMPROGRAMS\MentorAI\MentorAI.lnk" "$INSTDIR\MentorAI-Windows"
  CreateShortCut "$DESKTOP\MentorAI.lnk" "$INSTDIR\MentorAI-Windows"
  CreateShortCut "$SMPROGRAMS\MentorAI\Desinstalar.lnk" "$INSTDIR\uninstall.exe"
  
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MentorAI" "DisplayName" "MentorAI"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MentorAI" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MentorAI" "DisplayVersion" "1.0.0"
  
  MessageBox MB_OK "¡MentorAI instalado correctamente!"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\MentorAI-Windows"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\uninstall.exe"
  RMDir "$INSTDIR"
  
  Delete "$SMPROGRAMS\MentorAI\MentorAI.lnk"
  Delete "$SMPROGRAMS\MentorAI\Desinstalar.lnk"
  RMDir "$SMPROGRAMS\MentorAI"
  Delete "$DESKTOP\MentorAI.lnk"
  
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MentorAI"
SectionEnd
