$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$inputDoc = Join-Path $taskRoot 'outputs\Kich_ban_trinh_bay_demo_Web_RentalSystem.docx'
$qaFolder = Join-Path $taskRoot 'outputs\demo\docx-qa'
New-Item -ItemType Directory -Path $qaFolder -Force | Out-Null
$pdf = Join-Path $qaFolder 'Kich_ban_trinh_bay_demo_Web_RentalSystem.pdf'
$word = $null
$document = $null
$startedEmpty = $false
try {
    # Only open the new script, never the user's thesis document.
    $word = New-Object -ComObject Word.Application
    $startedEmpty = $word.Documents.Count -eq 0
    $oldAlerts = $word.DisplayAlerts
    if ($startedEmpty) { $word.Visible = $false }
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($inputDoc, $false, $true, $false)
    [void]$document.Fields.Update()
    $document.Repaginate()
    $pages = $document.ComputeStatistics(2)
    $document.ExportAsFixedFormat($pdf, 17)
    [ordered]@{ renderer='Microsoft Word'; source=$inputDoc; pdf=$pdf; pages=$pages; reason='Bundled render_docx.py has no LibreOffice executable on this Windows runtime' } |
        ConvertTo-Json | Set-Content (Join-Path $qaFolder 'render.json') -Encoding utf8
    Write-Output "Rendered $pages pages: $pdf"
} finally {
    if ($document) {
        $document.Close(0)
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($document)
    }
    if ($word) {
        $word.DisplayAlerts = $oldAlerts
        if ($startedEmpty -and $word.Documents.Count -eq 0) { $word.Quit() }
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($word)
    }
}
