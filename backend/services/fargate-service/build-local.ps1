#!/usr/bin/env pwsh
# Local build script for Fargate service
# Runs the same steps as the CI/CD pipeline for quick local testing

param(
    [switch]$SkipLint,
    [switch]$SkipBuild,
    [switch]$SkipPush,
    [string]$ImageTag = "local",
    [string]$AwsRegion = "",
    [string]$EcrRepository = "ece30861/model_eval_fargate"
)

$ErrorActionPreference = "Stop"
$ServiceRoot = $PSScriptRoot

# Get AWS credentials from environment (required unless skipping push)
if (-not $SkipPush) {
    if (-not $env:AWS_ACCESS_KEY_ID -or -not $env:AWS_SECRET_ACCESS_KEY) {
        Write-Host "ERROR: AWS credentials required for push. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables." -ForegroundColor Red
        Write-Host "Or use -SkipPush to build without pushing to ECR." -ForegroundColor Yellow
        exit 1
    }
    if (-not $AwsRegion -and -not $env:AWS_REGION) {
        Write-Host "ERROR: AWS region required for push. Set AWS_REGION environment variable or use -AwsRegion parameter." -ForegroundColor Red
        exit 1
    }
    $AwsRegion = if ($AwsRegion) { $AwsRegion } else { $env:AWS_REGION }
}

Write-Host "Starting Fargate Service Local Build" -ForegroundColor Cyan
Write-Host "Working directory: $ServiceRoot" -ForegroundColor Gray
Write-Host ""

# Step 1: Install dependencies
if (-not $SkipLint) {
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    python -m pip install --upgrade pip
    pip install -r "$ServiceRoot\requirements.txt"
    pip install flake8
    Write-Host "Dependencies installed" -ForegroundColor Green
    Write-Host ""

    # Step 2: Run linting
    Write-Host "Running flake8 linting..." -ForegroundColor Yellow
    
    Write-Host "  Critical errors check..." -ForegroundColor Gray
    flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics
    
    Write-Host "  Full lint check..." -ForegroundColor Gray
    flake8 src --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    Write-Host "Linting passed" -ForegroundColor Green
    Write-Host ""
}

# Step 3: Build Docker image
if (-not $SkipBuild) {
    Write-Host "Building Docker image..." -ForegroundColor Yellow
    
    # Check if Docker is running
    docker info > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Docker is not running. Please start Docker Desktop." -ForegroundColor Red
        exit 1
    }
    
    $ImageName = "fargate-service:$ImageTag"
    
    docker build -t $ImageName .
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker build failed" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Docker image built: $ImageName" -ForegroundColor Green
    Write-Host ""
    
    # Optional: Show image details
    Write-Host "Image details:" -ForegroundColor Yellow
    docker images $ImageName
    Write-Host ""
}

# Step 4: Push to ECR (default, unless skipped)
if (-not $SkipPush -and -not $SkipBuild) {
    Write-Host "Pushing to Amazon ECR..." -ForegroundColor Yellow
    
    # Get AWS account ID
    Write-Host "  Getting AWS account ID..." -ForegroundColor Gray
    $accountId = aws sts get-caller-identity --query Account --output text
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to get AWS account ID. Check your credentials." -ForegroundColor Red
        exit 1
    }
    
    # Get ECR registry URL
    $ecrRegistry = "$accountId.dkr.ecr.$AwsRegion.amazonaws.com"
    
    # Login to ECR
    Write-Host "  Logging into ECR ($ecrRegistry)..." -ForegroundColor Gray
    $password = aws ecr get-login-password --region $AwsRegion
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to get ECR password" -ForegroundColor Red
        exit 1
    }
    
    $password | docker login --username AWS --password-stdin $ecrRegistry
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: ECR login failed" -ForegroundColor Red
        exit 1
    }
    $ecrImageName = "$ecrRegistry/$EcrRepository"
    
    # Tag the image
    Write-Host "  Tagging image..." -ForegroundColor Gray
    docker tag "fargate-service:$ImageTag" "${ecrImageName}:${ImageTag}"
    docker tag "fargate-service:$ImageTag" "${ecrImageName}:latest"
    
    # Push both tags
    Write-Host "  Pushing ${ImageTag} tag..." -ForegroundColor Gray
    docker push "${ecrImageName}:${ImageTag}"
    
    Write-Host "  Pushing latest tag..." -ForegroundColor Gray
    docker push "${ecrImageName}:latest"
    
    Write-Host "Successfully pushed to ECR: ${ecrImageName}:${ImageTag}" -ForegroundColor Green
    Write-Host ""
}

Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host ""

if ($SkipPush) {
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  - Run the image: docker run --rm -e GITHUB_TOKEN=your_token fargate-service:$ImageTag" -ForegroundColor Gray
    Write-Host "  - Run with .env file: docker run --rm --env-file .env fargate-service:$ImageTag" -ForegroundColor Gray
    Write-Host "  - Run with tests: docker run --rm -e GITHUB_TOKEN=your_token fargate-service:$ImageTag pytest" -ForegroundColor Gray
    Write-Host "  - Push to ECR: .\build-local.ps1 -ImageTag $ImageTag" -ForegroundColor Gray
}
