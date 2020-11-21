#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

; Check if the downloads folder exists
if !InStr(FileExist("downloads"), "D"){
	MsgBox, Downloads folder not found. Run download_poe_tools.py first.
	ExitApp
}

PoBWorkingDIR := A_AppData . "\Path of Building Community"
FullFilePath := PoBWorkingDIR . "\Path of Building.exe"
if !FileExist(FullFilePath){
	MsgBox, Path of building not found. Run installer in the downloads folder
	ExitApp
}


EnvGet, LocalFolder, LOCALAPPDATA
AwakenedTradeDIR := LocalFolder . "\Programs\Awakened PoE Trade"
FullFilePath := AwakenedTradeDIR . "\Awakened PoE Trade.exe"
if !FileExist(FullFilePath){
	MsgBox, Awakened PoE trade not found. Run installer in the downloads folder
	ExitApp
}

if !FileExist("C:\Program Files (x86)\Grinding Gear Games\Path of Exile\PathOfExile_x64.exe"){
	MsgBox, You should install PoE.
	ExitApp
}

; Now that we know everything exists, run it.
Loop, Files, downloads\*.* 
	if A_LoopFileName contains poe-overlay,MercuryTrade
		Run, %A_LoopFileFullPath%
Run, %FullFilePath%, %PoBWorkingDIR%
Run, C:\Program Files (x86)\Grinding Gear Games\Path of Exile\PathOfExile_x64.exe, C:\Program Files (x86)\Grinding Gear Games\Path of Exile\