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