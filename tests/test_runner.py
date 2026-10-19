import subprocess
import os

html_path = os.path.abspath('index.html')
chrome = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
file_url = f'file:///{html_path.replace(os.sep, "/")}'
cmd = [chrome, '--headless=new', '--dump-dom', file_url]
res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
print('Return code:', res.returncode)
print('DOM length:', len(res.stdout))
print('Contains SOVEREIGN:', 'SOVEREIGN' in res.stdout)
print('Contains Adam Vega:', 'Adam Vega' in res.stdout)
