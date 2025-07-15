if ("$PWD" -ne "$PSScriptRoot") { exit 1 }

$pythonExe = Join-Path $PWD .venv\Scripts\python.exe

if (-not(Test-Path $pythonExe)) {
    python -m venv .venv
    . .venv\Scripts\Activate.ps1
    & $pythonExe -m pip install --upgrade pip
    & $pythonExe -m pip install -r requirements.txt
}

. .venv\Scripts\Activate.ps1
& $pythonExe -m nuitka --output-dir=dist app.py
