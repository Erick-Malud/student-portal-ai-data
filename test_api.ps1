# API Testing Script
# Make sure the server is running: uvicorn api.main:app --reload

$API_URL = "http://localhost:8000"
$API_KEY = "dev-api-key-change-in-production"

Write-Host "`n=== Testing Student Portal API ===" -ForegroundColor Green

# Test 1: Health Check
Write-Host "`n1. Health Check..." -ForegroundColor Yellow
curl.exe -X GET "$API_URL/" | ConvertFrom-Json | ConvertTo-Json -Depth 10

# Test 2: Get Student Profile
Write-Host "`n2. Get Student Profile (ID=1)..." -ForegroundColor Yellow
curl.exe -X GET "$API_URL/api/students/1" -H "X-API-Key: $API_KEY" | ConvertFrom-Json | ConvertTo-Json -Depth 10

# Test 3: Get Course Recommendations
Write-Host "`n3. Get Recommendations..." -ForegroundColor Yellow
$recommendBody = @{
    student_id = 1
    top_n = 3
    strategy = "hybrid"
} | ConvertTo-Json

curl.exe -X POST "$API_URL/api/recommend" `
    -H "X-API-Key: $API_KEY" `
    -H "Content-Type: application/json" `
    -d $recommendBody | ConvertFrom-Json | ConvertTo-Json -Depth 10

# Test 4: Sentiment Analysis
Write-Host "`n4. Sentiment Analysis..." -ForegroundColor Yellow
$sentimentBody = @{
    text = "This course is excellent! I really enjoyed it."
    include_emotions = $true
} | ConvertTo-Json

curl.exe -X POST "$API_URL/api/analysis/sentiment" `
    -H "X-API-Key: $API_KEY" `
    -H "Content-Type: application/json" `
    -d $sentimentBody | ConvertFrom-Json | ConvertTo-Json -Depth 10

# Test 5: Performance Prediction
Write-Host "`n5. Performance Prediction..." -ForegroundColor Yellow
$predictionBody = @{
    student_id = 1
    course = "Deep Learning"
} | ConvertTo-Json

curl.exe -X POST "$API_URL/api/predict/performance" `
    -H "X-API-Key: $API_KEY" `
    -H "Content-Type: application/json" `
    -d $predictionBody | ConvertFrom-Json | ConvertTo-Json -Depth 10

Write-Host "`n=== Tests Complete ===" -ForegroundColor Green
