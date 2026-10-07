@echo off
REM v1.1: finishes the OpenRouter free-tier run (nvidia/nemotron-3-ultra-550b-a55b:free on the
REM 200-ruling sample) independent of Claude Code. Resumable: every cached ruling is skipped, so
REM running it again after the sample is complete is a no-op. Meant to be run once a day by
REM Windows Task Scheduler until all 200 are cached.
REM scripts\run_new_models.py exits 0 when it finishes or when the daily free-request allowance
REM reaches 0 (a clean stop for the day). It exits 2 only if the OpenRouter key's `usage` rose
REM during a free-model run, which should never happen; Task Scheduler shows that as a failure.
REM Logs go to run_logs\openrouter_daily.log (gitignored), not to logs\.

cd /d "%~dp0.."
if not exist run_logs mkdir run_logs

echo [%date% %time%] Starting OpenRouter daily run >> run_logs\openrouter_daily.log
".venv\Scripts\python.exe" scripts\run_new_models.py --model "nvidia/nemotron-3-ultra-550b-a55b:free" >> run_logs\openrouter_daily.log 2>&1
echo [%date% %time%] OpenRouter daily run exited with code %errorlevel% >> run_logs\openrouter_daily.log
echo. >> run_logs\openrouter_daily.log

exit /b %errorlevel%
