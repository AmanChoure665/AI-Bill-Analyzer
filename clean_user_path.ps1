$u = [Environment]::GetEnvironmentVariable('Path','User')
Write-Output '---ORIGINAL USER PATH---'
Write-Output $u
$clean = $u -replace [char]34,''
Write-Output '---CLEANED USER PATH---'
Write-Output $clean
[Environment]::SetEnvironmentVariable('Path',$clean,'User')
Write-Output '---NEW USER PATH---'
Write-Output ([Environment]::GetEnvironmentVariable('Path','User'))
