<#
  render.ps1 — dựng lại toàn bộ hình vẽ của báo cáo từ mã nguồn PlantUML.

  Dựng cả sơ đồ PlantUML (.puml), biểu đồ số liệu (bieu-do.py, cần uv) và các sơ đồ
  vẽ theo toạ độ (so-do.py — Hình 2.2, 2.3, 2.6, 2.15, 2.16, 3.1, PL.1, PL.2, cần uv).

  Cách dùng (PowerShell, từ thư mục gốc repo hoặc bất kỳ đâu):
      .\baocao\hinh-ve\render.ps1              # dựng lại TẤT CẢ
      .\baocao\hinh-ve\render.ps1 chuong-2     # chỉ dựng lại một chương
      .\baocao\hinh-ve\render.ps1 -Dpi 300     # ảnh nét hơn để in

  Yêu cầu: Java (đã có sẵn, kiểm tra bằng `java -version`).
  Lần chạy đầu sẽ tự tải plantuml.jar về thư mục .tools/ (khoảng 22 MB, không commit vào Git).
#>
param(
  [string]$Scope = "",
  [int]$Dpi = 0
)

$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$ToolsDir = Join-Path $Here ".tools"
$Jar = Join-Path $ToolsDir "plantuml.jar"
$JarUrl = "https://repo1.maven.org/maven2/net/sourceforge/plantuml/plantuml/1.2024.7/plantuml-1.2024.7.jar"

if (-not (Test-Path $ToolsDir)) { New-Item -ItemType Directory -Path $ToolsDir | Out-Null }
if (-not (Test-Path $Jar)) {
  Write-Host "Chua co plantuml.jar - dang tai ve ..." -ForegroundColor Yellow
  Invoke-WebRequest -Uri $JarUrl -OutFile $Jar
  Write-Host "Da tai xong: $Jar" -ForegroundColor Green
}

$Target = if ($Scope) { Join-Path $Here $Scope } else { $Here }
$Files = Get-ChildItem -Path $Target -Filter *.puml -Recurse |
         Where-Object { $_.Name -ne "_style.puml" }

if ($Files.Count -eq 0) { Write-Host "Khong tim thay tep .puml nao trong $Target"; exit 0 }

Write-Host "Dang dung $($Files.Count) hinh ..." -ForegroundColor Cyan
# PLANTUML_LIMIT_SIZE: mac dinh 4096 px -> hinh lon bi CAT AM THAM. Nang len 12000.
$JavaArgs = @("-Dfile.encoding=UTF-8", "-DPLANTUML_LIMIT_SIZE=12000", "-jar", $Jar, "-charset", "UTF-8", "-tpng")
if ($Dpi -gt 0) { $JavaArgs += @("-SdefaultFontName=Arial", "-Sdpi=$Dpi") }
$JavaArgs += ($Files | ForEach-Object { $_.FullName })

& java @JavaArgs
if ($LASTEXITCODE -ne 0) { throw "PlantUML tra ve ma loi $LASTEXITCODE" }

# Bieu do so lieu (matplotlib) cua Chuong 1 va Chuong 3 — uv tu tao moi truong tam, khong cai gi vao du an.
if (-not $Scope -or $Scope -in @("chuong-1", "chuong-3")) {
  if (Get-Command uv -ErrorAction SilentlyContinue) {
    $env:PYTHONIOENCODING = "utf-8"
    & uv run --no-project --with matplotlib python (Join-Path $Here "bieu-do.py")
    if ($LASTEXITCODE -ne 0) { throw "bieu-do.py tra ve ma loi $LASTEXITCODE" }
  } else {
    Write-Host "Bo qua bieu do so lieu: chua cai uv (https://docs.astral.sh/uv/)" -ForegroundColor Yellow
  }
}

# So do ve theo toa do (matplotlib): Hinh 2.2, 2.3, 2.6, 2.15, 2.16, 3.1 va Phu luc PL.1, PL.2.
if (-not $Scope -or $Scope -in @("chuong-2", "chuong-3", "phu-luc")) {
  if (Get-Command uv -ErrorAction SilentlyContinue) {
    $env:PYTHONIOENCODING = "utf-8"
    & uv run --no-project --with matplotlib python (Join-Path $Here "so-do.py")
    if ($LASTEXITCODE -ne 0) { throw "so-do.py tra ve ma loi $LASTEXITCODE" }
  } else {
    Write-Host "Bo qua so do ve theo toa do: chua cai uv (https://docs.astral.sh/uv/)" -ForegroundColor Yellow
  }
}

Write-Host "Xong. Anh PNG nam canh tep .puml tuong ung." -ForegroundColor Green
Get-ChildItem -Path $Target -Filter *.png -Recurse |
  Sort-Object Name |
  ForEach-Object { "{0,-46} {1,6} KB" -f $_.Name, [int]($_.Length / 1KB) }
