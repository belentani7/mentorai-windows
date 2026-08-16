; MentorAI - Instalador NSIS para Windows
; Versión 1.0.0

!include "MUI2.nsh"
!include "x64.nsh"

; Configuración general
Name "MentorAI"
OutFile "..\dist\MentorAI-Installer.exe"
InstallDir "$PROGRAMFILES\MentorAI"
InstallDirRegKey HKLM "Software\MentorAI" "InstallDir"

; Configuración de MUI
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.md"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "Spanish"

; Secciones de instalación
Section "Instalar MentorAI"
  SetOutPath "$INSTDIR"
  
  ; Copiar archivos ejecutables
  File "dist\MentorAI-Linux"
  File "dist\MentorAI-Windows"
  
  ; Copiar base de conocimiento
  SetOutPath "$INSTDIR\knowledge_base"
  File "knowledge_base\*.json"
  
  ; Copiar documentación
  SetOutPath "$INSTDIR\docs"
  File "docs\*.md"
  
  ; Crear directorio de datos
  CreateDirectory "$APPDATA\MentorAI"
  
  ; Crear acceso directo en Inicio
  CreateDirectory "$SMPROGRAMS\MentorAI"
  CreateShortCut "$SMPROGRAMS\MentorAI\MentorAI.lnk" "$INSTDIR\MentorAI" "" "$INSTDIR\MentorAI" 0
  CreateShortCut "$SMPROGRAMS\MentorAI\Desinstalar.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  
  ; Crear acceso directo en escritorio
  CreateShortCut "$DESKTOP\MentorAI.lnk" "$INSTDIR\MentorAI" "" "$INSTDIR\MentorAI" 0
  
  ; Guardar información de instalación en registro
  WriteRegStr HKLM "Software\MentorAI" "InstallDir" "$INSTDIR"
  WriteRegStr HKLM "Software\MentorAI" "Version" "1.0.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MentorAI" "DisplayName" "MentorAI"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MentorAI" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MentorAI" "DisplayVersion" "1.0.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MentorAI" "Publisher" "MentorAI Project"
  
  ; Crear desinstalador
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  ; Mostrar mensaje de éxito
  MessageBox MB_OK "¡MentorAI ha sido instalado correctamente!$\n$\nPuedes encontrar el acceso directo en el menú Inicio y en el Escritorio."
SectionEnd

; Sección de desinstalación
Section "Uninstall"
  ; Eliminar archivos
  Delete "$INSTDIR\MentorAI"
  Delete "$INSTDIR\MentorAI-Windows"
  Delete "$INSTDIR\uninstall.exe"
  
  ; Eliminar directorios
  RMDir /r "$INSTDIR\knowledge_base"
  RMDir /r "$INSTDIR\docs"
  RMDir "$INSTDIR"
  
  ; Eliminar accesos directos
  Delete "$SMPROGRAMS\MentorAI\MentorAI.lnk"
  Delete "$SMPROGRAMS\MentorAI\Desinstalar.lnk"
  RMDir "$SMPROGRAMS\MentorAI"
  Delete "$DESKTOP\MentorAI.lnk"
  
  ; Eliminar entrada del registro
  DeleteRegKey HKLM "Software\MentorAI"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\MentorAI"
  
  MessageBox MB_OK "MentorAI ha sido desinstalado correctamente."
SectionEnd
