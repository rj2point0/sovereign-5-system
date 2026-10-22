@echo off
cd /d "c:\Users\User\5numsystem"
echo ======================================================== >> comment_task.log
echo [%date% %time%] Starting TikTok Comment Auto-Responder... >> comment_task.log
"C:\Users\User\AppData\Local\Programs\Python\Python312\python.exe" tiktok_comment_responder.py --live --limit 15 >> comment_task.log 2>&1
echo [%date% %time%] Run finished with exit code %ERRORLEVEL% >> comment_task.log
