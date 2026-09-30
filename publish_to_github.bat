@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

set "REPO_URL=https://github.com/telecomvibe111-cloud/Soviet-Union.git"

echo ===== Публикация проекта на GitHub =====
echo Репозиторий: %REPO_URL%
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

rem --- локальный репозиторий
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

rem --- привязка к репозиторию на GitHub (адрес всегда берётся из REPO_URL)
git remote get-url origin >nul 2>nul
if errorlevel 1 goto add_remote
git remote set-url origin "%REPO_URL%"
goto remote_ok
:add_remote
git remote add origin "%REPO_URL%"
:remote_ok

rem --- убираем .venv из индекса, если он туда попал раньше
git rm -r -q --cached .venv >nul 2>nul

rem --- коммит
git add .
git commit -m "Update %date% %time%"
echo.

rem --- отправка
git push -u origin main
if not errorlevel 1 goto success

echo.
echo Первая отправка не удалась. Пробую подтянуть файлы с GitHub и повторить...
git pull origin main --allow-unrelated-histories --no-edit
if errorlevel 1 goto failed
git push -u origin main
if errorlevel 1 goto failed

:success
echo.
echo ===== Готово! Код загружен на GitHub. =====
echo %REPO_URL:.git=%
goto end

:no_git
echo Git не найден. Установите его с https://git-scm.com/download/win
echo и запустите этот файл снова.
goto end

:failed
echo.
echo ===== Не удалось отправить код. =====
echo Частые причины:
echo  - репозиторий не существует или вы вошли в другой аккаунт GitHub
echo  - не пройден вход: запустите файл снова и войдите в браузере
echo  - конфликт файлов с GitHub: откройте проект в PyCharm и решите его в Git - Resolve Conflicts

:end
echo.
pause
