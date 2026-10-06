@echo off
REM Round 2, Task 1: runs the Gemini classification job independent of Claude Code.
REM Resumable via llm_logs/ caching -- safe to run repeatedly (a no-op once the
REM 200-ruling subset is complete, since every cached ruling is skipped). Intended to
REM be invoked daily by Windows Task Scheduler as a safety net (see
REM "schtasks" setup in DECISIONS.md / STATUS.md) in case any single run doesn't finish
REM the whole subset -- not because the free tier actually needs a full day between
REM requests (it doesn't; see DECISIONS.md, the real limit is 5 requests/minute).
REM Exits with whatever code scripts\run_gemini_classification.py exits with: 0 on a
REM clean finish (including "nothing left to do"), non-zero if it genuinely couldn't
REM get a response after its own retry budget -- Task Scheduler will show that as a
REM failed run, which is the correct, visible signal, not something to hide.

cd /d "%~dp0.."
if not exist logs mkdir logs

echo [%date% %time%] Starting Gemini daily run >> logs\gemini_daily.log
".venv\Scripts\python.exe" scripts\run_gemini_classification.py >> logs\gemini_daily.log 2>&1
echo [%date% %time%] Gemini daily run exited with code %errorlevel% >> logs\gemini_daily.log
echo. >> logs\gemini_daily.log

exit /b %errorlevel%
