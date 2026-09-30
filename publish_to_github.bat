@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo ===== Публикация проекта на GitHub =====
echo.

where git >nul 2>nul
if errorlevel 1 goto no_git

rem --- .gitignore, чтобы не выкладывать виртуальное окружение
if exist .gitignore goto has_ignore
echo .venv/> .gitignore
echo __pycache__/>> .gitignore
echo .idea/>> .gitignore
echo Создан файл .gitignore
:has_ignore

rem --- репозиторий
if exist .git goto has_repo
git init
:has_repo
git branch -M main

rem --- имя и почта для коммитов
set "GIT_NAME="
for /f "delims=" %%i in ('git config user.name') do set "GIT_NAME=%%i"
if defined GIT_NAME goto has_name
set /p "GIT_NAME=Введите ваше имя для коммитов: "
git config --global user.name "%GIT_NAME%"
:has_name

set "GIT_EMAIL="
for /f "delims=" %%i in ('git config user.email') do set "GIT_EMAIL=%%i"
if defined GIT_EMAIL goto has_email
set /p "GIT_EMAIL=Введите почту от аккаунта GitHub: "
git config --global user.email "%GIT_EMAIL%"
:has_email

rem --- адрес репозитория на GitHub
set "REMOTE="
for /f "delims=" %%i in ('git remote get-url origin 2^>nul') do set "REMOTE=%%i"
if defined REMOTE goto has_remote
echo.
echo Сначала создайте ПУСТОЙ репозиторий на https://github.com/new
echo Галочки README и .gitignore не ставьте.
echo.
set /p "REMOTE=Вставьте адрес репозитория вида https://github.com/логин/имя.git : "
if not defined REMOTE goto no_remote
git remote add origin "%REMOTE%"
:has_remote
echo.
echo Репозиторий: %REMOTE%
echo.

rem --- убираем .venv из индекса, если он туда попал раньше
git rm -r -q --cached .venv >nul 2>nul

rem --- коммит и отправка
git add .
git commit -m "Update project"
echo.
git push -u origin main
if errorlevel 1 goto push_failed

echo.
echo ===== Готово! Код загружен на GitHub. =====
goto end

:no_git
echo Git не найден. Установите его с https://git-scm.com/download/win
echo и запустите этот файл снова.
goto end

:no_remote
echo Адрес не введён. Запустите файл снова.
goto end

:push_failed
echo.
echo ===== Не удалось отправить код. =====
echo Частые причины:
echo  - репозиторий создан с README или .gitignore: создайте пустой
echo  - неверный адрес: проверьте его командой git remote -v
echo  - не пройден вход в GitHub: повторите запуск и войдите в браузере

:end
echo.
pause
