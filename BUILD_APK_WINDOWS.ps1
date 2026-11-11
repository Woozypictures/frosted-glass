param(
    [string]$SdkRoot = $env:ANDROID_HOME,
    [string]$KeystorePath = ""
)
$ErrorActionPreference = 'Stop'

function Require-Tool($Path, $Name) {
    if (-not (Test-Path -LiteralPath $Path)) { throw "Could not find $Name at: $Path`nInstall Android SDK Platform-Tools / Build-Tools in Android Studio SDK Manager." }
    return (Resolve-Path -LiteralPath $Path).Path
}

if ([string]::IsNullOrWhiteSpace($SdkRoot)) { $SdkRoot = $env:ANDROID_SDK_ROOT }
if ([string]::IsNullOrWhiteSpace($SdkRoot) -or -not (Test-Path -LiteralPath $SdkRoot)) {
    throw 'Set ANDROID_HOME (or ANDROID_SDK_ROOT) to your Android SDK folder, or pass -SdkRoot.'
}
$SdkRoot = (Resolve-Path -LiteralPath $SdkRoot).Path
$ProjectRoot = $PSScriptRoot
$Project = Join-Path $ProjectRoot 'proj'
if (-not (Test-Path (Join-Path $Project 'AndroidManifest.xml'))) { throw "Project folder not found: $Project" }

$Platforms = Get-ChildItem (Join-Path $SdkRoot 'platforms') -Directory -ErrorAction Stop | Where-Object { Test-Path (Join-Path $_.FullName 'android.jar') } | Sort-Object { try { [version]($_.Name -replace '^android-', '') } catch { [version]'0.0' } } -Descending
if (-not $Platforms) { throw 'No Android SDK platform found. Install an Android platform (API 23 or newer) using Android Studio > SDK Manager.' }
$AndroidJar = Join-Path $Platforms[0].FullName 'android.jar'
$BuildTools = Get-ChildItem (Join-Path $SdkRoot 'build-tools') -Directory -ErrorAction Stop | Sort-Object Name -Descending | Select-Object -First 1
if (-not $BuildTools) { throw 'No Android SDK Build-Tools found. Install Build-Tools using Android Studio > SDK Manager.' }
$Bt = $BuildTools.FullName
$aapt = Require-Tool (Join-Path $Bt 'aapt.exe') 'aapt'
$d8 = Require-Tool (Join-Path $Bt 'd8.bat') 'D8'
$zipalign = Require-Tool (Join-Path $Bt 'zipalign.exe') 'zipalign'
$apksigner = Require-Tool (Join-Path $Bt 'apksigner.bat') 'apksigner'

if ([string]::IsNullOrWhiteSpace($KeystorePath)) {
    $KeystorePath = Read-Host 'Path to Woozypictures_Release_Keystore_New.jks'
}
if (-not (Test-Path -LiteralPath $KeystorePath)) { throw "Keystore not found: $KeystorePath" }
$KeystorePath = (Resolve-Path -LiteralPath $KeystorePath).Path
$Alias = 'woozypictures-release'

$Work = Join-Path $ProjectRoot 'apk_build'
$Gen = Join-Path $Work 'gen'
$Obj = Join-Path $Work 'obj'
$DexOut = Join-Path $Work 'dex'
New-Item -ItemType Directory -Force -Path $Work,$Gen,$Obj,$DexOut | Out-Null
Get-ChildItem $Obj -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem $Gen -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem $DexOut -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force

$Unsigned = Join-Path $Work 'unsigned.apk'
$Aligned = Join-Path $Work 'aligned.apk'
$Signed = Join-Path $ProjectRoot 'Frosted_Glass_Icon_Pack.apk'
$ClassesJar = Join-Path $Work 'classes.jar'

Push-Location $Project
try {
    Write-Host "Using Android platform: $($Platforms[0].Name)"
    Write-Host "Using Build-Tools: $($BuildTools.Name)"
    Write-Host 'Packaging resources...'
    & $aapt package -f -m --no-crunch -0 arsc -J $Gen -M 'AndroidManifest.xml' -S 'res' -A 'assets' -I $AndroidJar -F $Unsigned
    if ($LASTEXITCODE -ne 0) { throw 'aapt resource packaging failed.' }

    Write-Host 'Compiling Java source...'
    $JavaFile = Join-Path $Project 'src/com/woozypictures/frostedglass/MainActivity.java'
    & javac -encoding UTF-8 -source 8 -target 8 -bootclasspath $AndroidJar -d $Obj -sourcepath ((Join-Path $Project 'src') + ';' + $Gen) $JavaFile
    if ($LASTEXITCODE -ne 0) { throw 'javac compilation failed.' }

    Write-Host 'Converting classes to DEX...'
    & jar --create --file $ClassesJar -C $Obj .
    if ($LASTEXITCODE -ne 0) { throw 'Could not package compiled Java classes.' }
    & $d8 --release --min-api 21 --lib $AndroidJar --output $DexOut $ClassesJar
    if ($LASTEXITCODE -ne 0) { throw 'D8 conversion failed.' }

    Write-Host 'Adding DEX and aligning APK...'
    Copy-Item $Unsigned (Join-Path $ProjectRoot 'unsigned_temp.apk') -Force
    Push-Location $DexOut
    try { & $aapt add (Join-Path $ProjectRoot 'unsigned_temp.apk') 'classes.dex' } finally { Pop-Location }
    if ($LASTEXITCODE -ne 0) { throw 'Could not add classes.dex to the APK.' }
    & $zipalign -f -p 4 (Join-Path $ProjectRoot 'unsigned_temp.apk') $Aligned
    if ($LASTEXITCODE -ne 0) { throw 'zipalign failed.' }

    Write-Host 'Signing APK. Android SDK will prompt for the keystore/key password; it is not stored by this script.'
    & $apksigner sign --ks $KeystorePath --ks-key-alias $Alias --out $Signed $Aligned
    if ($LASTEXITCODE -ne 0) { throw 'APK signing failed.' }
    & $apksigner verify --verbose --print-certs $Signed
    if ($LASTEXITCODE -ne 0) { throw 'APK signature verification failed.' }

    Write-Host "`nSUCCESS: $Signed" -ForegroundColor Green
}
finally {
    Pop-Location
    Remove-Item (Join-Path $ProjectRoot 'unsigned_temp.apk') -Force -ErrorAction SilentlyContinue
}
