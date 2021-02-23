;Pharmaship installer
;--------------------------------
;Constants
!define APPNAME "Pharmaship"
!define COMPANYNAME "Association DSM"
!define DESCRIPTION "A ship's medical chest inventory software"
# These three must be integers
!define VERSIONMAJOR 0
!define VERSIONMINOR 1
!define VERSIONBUILD 0
# These will be displayed by the "Click here for support information" link in "Add/Remove Programs"
# It is possible to use "mailto:" links in here to open the email client
!define HELPURL "http://pharmaship.devmaretique.com" # "Support Information" link
!define UPDATEURL "http://pharmaship.devmaretique.com/releases" # "Product Updates" link
!define ABOUTURL "http://devmaretique.com" # "Publisher" link

!define INSTDIR_REG_ROOT "HKLM"
!define INSTDIR_REG_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"

Unicode True

;--------------------------------
;Include Modern UI
!include "MUI2.nsh"
;Includes for custom page and logic
!include "nsDialogs.nsh"
!include "LogicLib.nsh"
;--------------------------------
;Include Advanced Uninstall Log NSIS Header
!include "AdvUninstLog.nsh"

;--------------------------------
;General

;Name and file
Name "${APPNAME}"
Icon "pharmaship.ico"
OutFile "pharmaship_setup_x64.exe"
ShowInstDetails show
ShowUninstDetails show

;Default installation folder
InstallDir "$LOCALAPPDATA\${APPNAME}"

;Get installation folder from registry if available

;InstallDir "$PROGRAMFILES\${APP_NAME}"
InstallDirRegKey ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}" "InstallDir"

;Request application privileges for Windows Vista
RequestExecutionLevel user

;--------------------------------
;Interface Configuration
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "pharmaship_installer.bmp" ; optional
!define MUI_ABORTWARNING

;--------------------------------
;Pages
Var StartMenuFolder
!insertmacro UNATTENDED_UNINSTALL
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\LICENSE"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_STARTMENU 0 $StartMenuFolder
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
UninstPage custom un.DeleteUserData un.DeleteUserDataLeave ;Custom page
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;Allowance macro
!macro Allowance filename
  CreateDirectory $INSTDIR\allowances
  File "/oname=$INSTDIR\allowances\${filename}" "..\allowances\${filename}"
  nsExec::ExecToLog '"$INSTDIR\pharmaship-admin.exe" "import" "$INSTDIR\allowances\${filename}"'
!macroend

;--------------------------------
;Languages

!insertmacro MUI_LANGUAGE "English"

!define UNINSTALLOG_LOCALIZE ;if you define this you have to provide language strings to use

LangString UNLOG_HEADER ${LANG_ENGLISH} "=========== Uninstaller Log please do not edit this file ==========="
LangString UNLOG_DAT_NOT_FOUND ${LANG_ENGLISH} "${UNINST_DAT} not found, unable to perform uninstall."
LangString UNLOG_DEL_FILE ${LANG_ENGLISH} 'Delete File "$R9"?'
LangString UNLOG_DEL_DIR ${LANG_ENGLISH} 'Delete Directory "$R9"?'
LangString UNLOG_EMPTY_DIR ${LANG_ENGLISH} "Previous installation detected at $0.$\n\
                              Required file ${UNINSTALL_LOG}.dat is missing.$\n$\n\
                              It is highly recommended to select an \
                              empty directory and perform a fresh \
                              installation."
LangString UNLOG_ERROR_LOG ${LANG_ENGLISH} "Error in log ${UNINSTALL_LOG}."
LangString UNLOG_ERROR_CREATE ${LANG_ENGLISH} "Error creating ${UNINSTALL_LOG}."

;Language strings
LangString DESC_SecPharmaship ${LANG_ENGLISH} "Install Pharmaship software."
LangString DESC_SecAllowances ${LANG_ENGLISH} "Install additional allowances packages."
LangString DESC_SecDesktopLnk ${LANG_ENGLISH} "Create a shortcut on the desktop."

;--------------------------------
;Installer Sections
Section "Pharmaship software" SecPharmaship

  SetOutPath "$INSTDIR"

  SectionIn RO

  !insertmacro UNINSTALL.LOG_OPEN_INSTALL
    File "..\build\win64\"
    File "pharmaship.ico"
  !insertmacro UNINSTALL.LOG_CLOSE_INSTALL

  File /r "..\build\win64\share"
  File /r "..\build\win64\lib"
  File /r "..\build\win64\etc"

  ;Store installation folder
  WriteRegStr HKCU "Software\${APPNAME}" "" $INSTDIR

  # Start Menu
  !insertmacro MUI_STARTMENU_WRITE_BEGIN 0 ;This macro sets $StartMenuFolder and skips to MUI_STARTMENU_WRITE_END if the "Don't create shortcuts" checkbox is checked...
    CreateDirectory "$SMPrograms\$StartMenuFolder"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Pharmaship.lnk" "$INSTDIR\pharmaship.exe"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  !insertmacro MUI_STARTMENU_WRITE_END

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  WriteRegStr ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}" "DisplayName" "$\"${APPNAME} - ${DESCRIPTION}$\""
  WriteRegStr ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
  WriteRegStr ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
  WriteRegStr ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}" "InstallLocation" "$\"$INSTDIR$\""
  WriteRegStr ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}" "DisplayIcon" "$\"$INSTDIR\pharmaship.ico$\""
  WriteRegStr ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}" "Publisher" "$\"${COMPANYNAME}$\""
  WriteRegStr ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}" "HelpLink" "$\"${HELPURL}$\""
  WriteRegStr ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}" "URLUpdateInfo" "$\"${UPDATEURL}$\""
  WriteRegStr ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}" "URLInfoAbout" "$\"${ABOUTURL}$\""
  WriteRegStr ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}" "DisplayVersion" "$\"${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}$\""
  WriteRegDWORD ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}" "VersionMajor" ${VERSIONMAJOR}
  WriteRegDWORD ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}" "VersionMinor" ${VERSIONMINOR}

  ;Run Pharmaship configuration scripts
  nsExec::ExecToLog '"$INSTDIR\pharmaship-admin.exe" "migrate"'
  nsExec::ExecToLog '"$INSTDIR\pharmaship-admin.exe" "populate"'

SectionEnd

SectionGroup "Allowances" SecAllowances



  ;Run allowance installation scripts
  Section "!Dotation A - 25 pers"
    !insertmacro Allowance "allowance_dotation-a-25-marins_120a.tar.asc"
  SectionEnd

  Section "!GSMU 2018"
    !insertmacro Allowance "allowance_gsmu_2018.tar.asc"
  SectionEnd

  ; Section /o "CMA CGM V12"
  ;   !insertmacro Allowance "allowance_cma-cgm_v12.tar.asc"
  ; SectionEnd

  ; Section /o "MARLINK"
  ;   !insertmacro Allowance "allowance_marlink-telemed_01.tar.asc"
  ; SectionEnd
  ;
  ; Section /o "POCrame"
  ;   !insertmacro Allowance "allowance_pocrame_01.tar.asc"
  ; SectionEnd

SectionGroupEnd


Section "Desktop Shortcut" SecDesktopLnk
  CreateShortCut "$DESKTOP\Pharmaship.lnk" "$INSTDIR\pharmaship.exe"
SectionEnd

;--------------------------------
;Descriptions

;Assign language strings to sections
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${SecPharmaship} $(DESC_SecPharmaship)
!insertmacro MUI_DESCRIPTION_TEXT ${SecAllowances} $(DESC_SecAllowances)
!insertmacro MUI_DESCRIPTION_TEXT ${SecDesktopLnk} $(DESC_SecDesktopLnk)
!insertmacro MUI_FUNCTION_DESCRIPTION_END


Function .onInit
  !insertmacro UNINSTALL.LOG_PREPARE_INSTALL
FunctionEnd

Function .onInstSuccess
  !insertmacro UNINSTALL.LOG_UPDATE_INSTALL
FunctionEnd

;--------------------------------
; Uninstaller Section
Var Dialog
Var Checkbox
Var Checkbox_State

Section Uninstall
  SetDetailsPrint "both"

  RMDir /r "$INSTDIR\lib"
  RMDir /r "$INSTDIR\share"
  RMDir /r "$INSTDIR\etc"
  RMDir /r "$INSTDIR\allowances"

  !insertmacro UNINSTALL.LOG_UNINSTALL "$INSTDIR"
  !insertmacro UNINSTALL.LOG_END_UNINSTALL

  DeleteRegKey /ifempty ${INSTDIR_REG_ROOT} "${INSTDIR_REG_KEY}"

  Delete "$INSTDIR\pharmaship.ico"

  # Delete user data if checkbox checked
  ${If} $Checkbox_State == ${BST_CHECKED}
		RMDir /r "$LOCALAPPDATA\pharmaship"
	${EndIf}

  # Last $INSTDIR files to delete
  Delete "$INSTDIR\Uninstall.exe"

  # Delete Start Menu
  !insertmacro MUI_STARTMENU_WRITE_BEGIN 0 ;This macro sets $StartMenuFolder and skips to MUI_STARTMENU_WRITE_END if the "Don't create shortcuts" checkbox is checked...
    Delete "$SMPROGRAMS\$StartMenuFolder\Pharmaship.lnk"
    Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk"
    RMDir "$SMPrograms\$StartMenuFolder"
  !insertmacro MUI_STARTMENU_WRITE_END

  # Delete shortcut if any
  Delete "$DESKTOP\Pharmaship.lnk"

  # Delete Registry keys
  DeleteRegKey /ifempty HKCU "Software\Pharmaship"
  DeleteRegKey ${INSTDIR_REG_ROOT} ${INSTDIR_REG_KEY}

SectionEnd

Function UN.onInit
  !insertmacro UNINSTALL.LOG_BEGIN_UNINSTALL
FunctionEnd

; Function un.DeleteUserData
Function un.DeleteUserData

	nsDialogs::Create 1018
	Pop $Dialog

	${If} $Dialog == error
		Abort
	${EndIf}

	${NSD_CreateCheckbox} 0 30u 100% 10u "&Delete user data (including inventories)"
	Pop $Checkbox

	${If} $Checkbox_State == ${BST_CHECKED}
		${NSD_Check} $Checkbox
	${EndIf}

	# alternative for the above ${If}:
	#${NSD_SetState} $Checkbox_State

	nsDialogs::Show

FunctionEnd

Function un.DeleteUserDataLeave
    ${NSD_GetState} $Checkbox $Checkbox_State
FunctionEnd
