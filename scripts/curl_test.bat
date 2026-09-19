@echo off
rem Sends a screenshot + question to llama-server using curl (Mini-project B criterion).
rem The request file is made by the smoke test (START-HERE option 3).
cd /d "%~dp0.."
if not exist "results\curl_request.json" (
  echo Run the smoke test first ^(START-HERE option 3^) - it creates results\curl_request.json
  pause
  exit /b 1
)
echo Sending image + prompt with curl...
echo.
curl.exe -s http://127.0.0.1:8081/v1/chat/completions -H "Content-Type: application/json" -d @results\curl_request.json
echo.
echo.
echo Look for "content": "..." above - that is the model's answer. "timings" shows the speed.
pause
