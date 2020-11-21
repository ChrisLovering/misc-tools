#NoEnv
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
Menu, Tray, Icon, shell32.dll, 44 ; Sets the system tray icon to a star, to differentiate from other ahk scripts

;Open windows terminal
^!t::
Run wt
return

;Open default app page
^!r::
Run ms-settings:defaultapps
return

;Open windows update
^!u::
Run ms-settings:windowsupdate
return

;Simulate keyboard input of clipboard, for programs that don't let you paste
^!v::
Send, %Clipboard%
return

#IfWinActive, ahk_class POEWindowClass
`::
{
	;Initialize random delays (arbitrary values, change if you want)
	random, delay2, 10, 30
	random, delay3, 10, 30
	random, delay4, 10, 30
	random, delay5, 10, 30

	send, 1 ;simulates the keypress of the 1 button. If you use another button, change it!

	sleep, %delay2%
	send, 2 ;simulates the keypress of the 2 button. If you use another button, change it!

	sleep, %delay3%
	send, 3 ;simulates the keypress of the 3 button. If you use another button, change it!

	sleep, %delay4%
	send, 4 ;simulates the keypress of the 4 button. If you use another button, change it!

	sleep, %delay5%
	send, 5 ;simulates the keypress of the 5 button. If you use another button, change it!
}
return

#IfWinActive, ahk_class POEWindowClass
]::
{
	random, delay1, 10, 30
	random, delay2, 10, 30
	random, delay3, 10, 30
	send, {shift down}
	sleep, %delay1%
	send, {lbutton down}
	send, {lbutton up}
	sleep, %delay2%
	send, {shift up}
	sleep, %delay3%
	send, {enter}
}
return