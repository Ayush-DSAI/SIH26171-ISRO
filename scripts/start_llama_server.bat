@echo off
rem ==========================================================
rem  Starts the local VLM server (Qwen3.5-4B on your RTX 4070)
rem  Keep this window OPEN while the team uses the model.
rem  To stop it: click this window and press Ctrl+C.
rem  Usage: start_llama_server.bat          (only this laptop)
rem         start_llama_server.bat share    (teammates on same Wi-Fi / Tailscale)
rem ==========================================================
cd /d "%~dp0.."
if not exist ".env" (
  echo [FAIL] .env file missing. Run START-HERE.bat option 1 first.
  pause
  exit /b 1
)
for /f "usebackq eol=# tokens=1,* delims==" %%A in (".env") do set "%%A=%%B"

set "HOST=127.0.0.1"
if /i "%~1"=="share" set "HOST=0.0.0.0"
set "PORT=8081"
for /f "tokens=3 delims=:/" %%P in ("%LLAMA_SERVER_URL%") do set "PORT=%%P"
set "KEYARG="
if /i "%~1"=="share" if defined LLAMA_API_KEY set "KEYARG=--api-key %LLAMA_API_KEY%"

if not exist "%LLAMA_SERVER_EXE%" (
  echo [FAIL] llama-server.exe not found at %LLAMA_SERVER_EXE%
  echo        Run START-HERE.bat option 1 - setup.
  pause
  exit /b 1
)
if not exist "%MODEL_PATH%" (
  echo [FAIL] Model file not found: %MODEL_PATH%
  echo        Run START-HERE.bat option 1 - setup.
  pause
  exit /b 1
)

title VLM SERVER - keep this window open
echo.
echo  ============================================================
echo    VLM SERVER STARTING  -  Qwen3.5-4B  on  %HOST%:%PORT%
echo  ============================================================
echo    Wait until you see:  "server is listening on http://..."
echo    Then it is READY.  Do NOT close this window.
echo    Web chat:  http://127.0.0.1:%PORT%     Stop: press Ctrl+C
if /i "%~1"=="share" echo    SHARED MODE: teammates use http://YOUR-IP:%PORT%
if /i "%~1"=="share" if not defined LLAMA_API_KEY echo    [!!] No LLAMA_API_KEY in .env - anyone on your network can use it.
echo  ============================================================
echo.

"%LLAMA_SERVER_EXE%" -m "%MODEL_PATH%" --mmproj "%MMPROJ_PATH%" --host %HOST% --port %PORT% -c %CTX_SIZE% -ngl %N_GPU_LAYERS% -np 1 %KEYARG%

echo.
echo  The server stopped. If you did not press Ctrl+C, read the red lines above
echo  and check the Troubleshooting section of the guide.
pause
