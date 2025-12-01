# Local Lambda build script
# Mimics the CI/CD build process

Write-Host "Starting Lambda build process..." -ForegroundColor Green

# Navigate to lambda-service directory
Set-Location $PSScriptRoot

# Clean up any existing lib directory
Write-Host "Cleaning up existing lib directory..." -ForegroundColor Yellow
if (Test-Path lib) {
    Remove-Item -Recurse -Force lib
}

# Copy shared lib directory from backend
Write-Host "Copying shared lib directory..." -ForegroundColor Yellow
Copy-Item -Recurse ..\..\lib .\lib

# Clean previous build
Write-Host "Cleaning previous build..." -ForegroundColor Yellow
if (Test-Path .aws-sam\build) {
    Remove-Item -Recurse -Force .aws-sam\build
}

# Build with SAM
Write-Host "Building Lambda function with SAM..." -ForegroundColor Green
sam build

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To deploy, run: sam deploy --config-file samconfig.toml" -ForegroundColor Cyan
} else {
    Write-Host "Build failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}

# Clean up the copied lib after build (SAM already packaged it)
Write-Host "Cleaning up copied lib directory..." -ForegroundColor Yellow
Remove-Item -Recurse -Force lib

Write-Host "Done!" -ForegroundColor Green
