# git-sync.ps1 - Hỗ trợ Commit và Push đồng bộ với Jira
# Sử dụng: ./scripts/git-sync.ps1

Write-Host "--- Git & Jira Sync Tool ---" -ForegroundColor Cyan

# 1. Nhập mã Jira
$jiraId = Read-Host "Nhập mã Jira Issue (ví dụ: SCRUM-1)"
if (-not $jiraId) { 
    Write-Host "Lỗi: Bạn phải nhập mã Jira!" -ForegroundColor Red
    exit 
}

# 2. Nhập thông điệp commit
$message = Read-Host "Nhập thông điệp commit"
if (-not $message) { 
    Write-Host "Lỗi: Thông điệp commit không được để trống!" -ForegroundColor Red
    exit 
}

# 3. Lệnh (Tùy chọn)
$command = Read-Host "Lệnh Jira (ví dụ: #done, #time 1h - Bỏ trống nếu không cần)"

# Tạo commit message hoàn chỉnh
$fullMessage = "$jiraId $command $message"

Write-Host "`nĐang thực thi các lệnh Git..." -ForegroundColor Yellow

# Thực hiện Git
git add .
git commit -m "$fullMessage"
$branch = git branch --show-current
git push origin $branch

Write-Host "`n--- Done! Synced with Jira: $jiraId ---" -ForegroundColor Green
