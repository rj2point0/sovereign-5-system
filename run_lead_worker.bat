@echo off
cd /d "c:\Users\User\5numsystem"
"C:\Users\User\AppData\Local\Programs\Python\Python312\python.exe" lead_capture_worker.py --poll-once >> lead_worker.log 2>&1
