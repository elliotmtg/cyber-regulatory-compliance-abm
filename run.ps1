param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ScriptArgs
)
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
& "$dir\.venv\Scripts\python.exe" "$dir\run.py" @ScriptArgs
