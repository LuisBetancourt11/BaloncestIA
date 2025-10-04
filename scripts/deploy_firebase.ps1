param(
  [string]$firebaseProject = "baloncestoia-e0724"
)

Write-Host "Authenticating with Firebase..."
firebase login

Write-Host "Using Firebase project: $firebaseProject"
firebase use $firebaseProject

Write-Host "Deploying Firebase Hosting..."
firebase deploy --only hosting

Write-Host "Firebase Hosting deploy finished. Check console.firebase.google.com for details."
