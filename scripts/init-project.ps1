<#
.SYNOPSIS
  One-time initialisation: replaces every __TOKEN__ in this repository with your values.

.DESCRIPTION
  1. Reads config\platform.env. Any value still equal to its token is asked interactively
     (or taken from -Values).
  2. Replaces the tokens in every text file under the repo (skips .git\, runs\, binaries and
     this script's own folder entries listed in $SkipFiles).
  3. Writes config\.initialized with the values and a timestamp.
  Re-running after initialisation is a no-op unless -Force is given.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\init-project.ps1
  powershell -ExecutionPolicy Bypass -File scripts\init-project.ps1 -Values @{PLATFORM_NAME='PayCore';DEVCTL='pctl';AI_PLATFORM='Atlas';CODE_ROOT='D:\work\paycore';DESIGN_DOCS_ROOT='D:\work\design-docs'}
#>
[CmdletBinding()]
param(
  [hashtable]$Values = @{},
  [switch]$Force,
  [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$EnvFile  = Join-Path $RepoRoot 'config\platform.env'
$Marker   = Join-Path $RepoRoot 'config\.initialized'
$Tokens   = @('PLATFORM_NAME','DEVCTL','AI_PLATFORM','CODE_ROOT','DESIGN_DOCS_ROOT')
$TextExt  = @('.md','.yaml','.yml','.json','.env','.txt','.html','.py','.sh','.ps1','.cmd','.sql','.gitignore','.gitattributes')
$SkipDirs = @('.git','runs','node_modules','__pycache__')
$SkipFiles = @('init-project.ps1','init-project.sh','init-project.py')

if ((Test-Path $Marker) -and -not $Force) {
  Write-Host "Already initialised ($Marker). Use -Force to re-run." -ForegroundColor Yellow
  exit 0
}

# --- 1. collect values -------------------------------------------------------
$current = @{}
Get-Content $EnvFile | ForEach-Object {
  if ($_ -match '^\s*([A-Z_]+)\s*=\s*(.*)$') { $current[$Matches[1]] = $Matches[2].Trim() }
}
foreach ($t in $Tokens) {
  $v = $null
  if ($Values.ContainsKey($t)) { $v = [string]$Values[$t] }
  elseif ($current.ContainsKey($t) -and $current[$t] -ne "__${t}__" -and $current[$t] -ne '') { $v = $current[$t] }
  while ([string]::IsNullOrWhiteSpace($v)) {
    $v = Read-Host "Value for $t"
  }
  $Values[$t] = $v
}
foreach ($p in 'CODE_ROOT','DESIGN_DOCS_ROOT') {
  if (-not (Test-Path $Values[$p])) { Write-Warning "$p path does not exist yet: $($Values[$p]) (continuing)" }
}

Write-Host "`nValues:" -ForegroundColor Cyan
foreach ($t in $Tokens) { Write-Host ("  {0,-18} = {1}" -f $t, $Values[$t]) }
if ($DryRun) { Write-Host "`n-DryRun: no files changed."; exit 0 }

# --- 2. replace --------------------------------------------------------------
$changed = 0
Get-ChildItem -Path $RepoRoot -Recurse -File -Force | Where-Object {
  $rel = $_.FullName.Substring($RepoRoot.Length).TrimStart('\','/')
  $top = ($rel -split '[\\/]')[0]
  ($SkipDirs -notcontains $top) -and ($SkipFiles -notcontains $_.Name) -and ($TextExt -contains $_.Extension.ToLower() -or $_.Name -eq '.gitignore')
} | ForEach-Object {
  $text = [System.IO.File]::ReadAllText($_.FullName)
  $new = $text
  foreach ($t in $Tokens) { $new = $new.Replace("__${t}__", $Values[$t]) }
  if ($new -ne $text) {
    [System.IO.File]::WriteAllText($_.FullName, $new, (New-Object System.Text.UTF8Encoding($false)))
    $changed++
    Write-Host "  updated $($_.FullName.Substring($RepoRoot.Length+1))"
  }
}

# --- 3. marker ---------------------------------------------------------------
$stamp = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
$lines = @("initialized_at=$stamp") + ($Tokens | ForEach-Object { "$_=$($Values[$_])" })
Set-Content -Path $Marker -Value $lines -Encoding UTF8
Write-Host "`nDone. $changed file(s) updated. Marker written: config\.initialized" -ForegroundColor Green
Write-Host "Next: python scripts\sync-agents.py  then open prompts\00-discover.md"
