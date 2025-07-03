# PowerShell wrapper for Gemini CLI
# Provides robust cross-platform execution on Windows

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

# Function to find Gemini executable
function Find-GeminiExecutable {
    # Check GEMINI_CLI_PATH environment variable
    if ($env:GEMINI_CLI_PATH) {
        $candidates = @(
            Join-Path $env:GEMINI_CLI_PATH "gemini.cmd",
            Join-Path $env:GEMINI_CLI_PATH "gemini.exe",
            Join-Path $env:GEMINI_CLI_PATH "gemini.bat",
            $env:GEMINI_CLI_PATH
        )
        
        foreach ($path in $candidates) {
            if (Test-Path $path) {
                return $path
            }
        }
    }
    
    # Search in PATH
    $geminiInPath = Get-Command -Name gemini -ErrorAction SilentlyContinue
    if ($geminiInPath) {
        return $geminiInPath.Source
    }
    
    # Check common installation locations
    $searchPaths = @(
        "$env:APPDATA\npm\gemini.cmd",
        "$env:APPDATA\npm\gemini.exe",
        "$env:LOCALAPPDATA\Programs\claif\bin\gemini.cmd",
        "$env:LOCALAPPDATA\Programs\claif\bin\gemini.exe",
        "$env:USERPROFILE\.local\bin\gemini.cmd",
        "$env:USERPROFILE\.local\bin\gemini.exe"
    )
    
    foreach ($path in $searchPaths) {
        if (Test-Path $path) {
            return $path
        }
    }
    
    # Check if npm is available and try to find via npm
    $npmCmd = Get-Command -Name npm -ErrorAction SilentlyContinue
    if ($npmCmd) {
        try {
            $npmRoot = & npm root -g 2>$null
            if ($npmRoot) {
                $npmGemini = Join-Path $npmRoot "..\@google\gemini-cli\bin\gemini"
                if (Test-Path $npmGemini) {
                    return $npmGemini
                }
            }
        } catch {
            # Ignore npm errors
        }
    }
    
    # Check if bun is available
    $bunCmd = Get-Command -Name bun -ErrorAction SilentlyContinue
    if ($bunCmd) {
        try {
            $bunPath = & bun pm bin -g 2>$null
            if ($bunPath) {
                $bunGemini = Join-Path $bunPath "gemini"
                if (Test-Path $bunGemini) {
                    return $bunGemini
                }
            }
        } catch {
            # Ignore bun errors
        }
    }
    
    return $null
}

# Main execution
$geminiExe = Find-GeminiExecutable

if (-not $geminiExe) {
    Write-Error "Gemini CLI not found."
    Write-Host ""
    Write-Host "Please install Gemini CLI using one of these methods:"
    Write-Host "  npm install -g @google/gemini-cli"
    Write-Host "  bun add -g @google/gemini-cli"
    Write-Host "  claif install gemini"
    Write-Host ""
    Write-Host "Or set GEMINI_CLI_PATH environment variable to the installation directory."
    exit 1
}

# Execute Gemini with all arguments
try {
    & $geminiExe @Arguments
    exit $LASTEXITCODE
} catch {
    Write-Error "Failed to execute Gemini CLI: $_"
    exit 1
}