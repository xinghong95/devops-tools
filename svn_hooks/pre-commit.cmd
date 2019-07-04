@echo off

set REPOS=%1 
set TXN=%2 
set SVNLOOK="D:\VisualSVN Server\bin\svnlook.exe"
set PYTHON="D:\Python27\python.exe"

%SVNLOOK% log -t %2 %1 > %1/log_msg_%2.txt

%PYTHON% E:\Repositories\test\hooks\check.py %1 %2 2 > nul
