param(
  [string]$repoName = "BaloncestIA",
  [string]$visibility = "public",
  [string]$remoteName = "origin"
)

function Write-Info($m){ Write-Host $m -ForegroundColor Cyan }
function Write-Err($m){ Write-Host $m -ForegroundColor Red }

Write-Info "This script will try to create a GitHub repo using the 'gh' CLI and push the current folder."

if (-not (Test-Path .git)){
  Write-Info "Initializing local git repository..."
  git init
  git add .
  git commit -m "Initial commit"
}

$gh = Get-Command gh -ErrorAction SilentlyContinue
if ($gh) {
  Write-Info "Found gh CLI. Creating repository '$repoName' (visibility: $visibility) via gh..."
  gh repo create $repoName --$visibility --source=. --remote-name $remoteName --confirm
  if ($LASTEXITCODE -ne 0) { Write-Err "gh repo create failed. Check gh auth status."; exit 1 }
  Write-Info "Pushing to GitHub..."
  git push -u $remoteName main
  Write-Info "Done. Repo created and pushed."
} else {
  Write-Info "gh CLI not found. I will print manual commands to run."
  Write-Host "1) Create a repository on GitHub (https://github.com/new) named: $repoName" -ForegroundColor Yellow
  Write-Host "2) Then run (replace YOUR_REMOTE_URL):" -ForegroundColor Yellow
  Write-Host "   git remote add $remoteName https://github.com/YOUR_GH_USER/$repoName.git" -ForegroundColor Green
  Write-Host "   git branch -M main" -ForegroundColor Green
  Write-Host "   git push -u $remoteName main" -ForegroundColor Green
}
