param(
    [Parameter(Mandatory = $true)]
    [string]$SourceFile,

    [string]$DestinationRoot,

    [string]$ImageRoot,

    [string]$SheetName,

    [string]$CategoryColumn = "category",

    [string]$ProductColumn = "product",

    [string]$ImagesColumn = "images",

    [string]$CategorySlugColumn = "category_slug",

    [string]$ProductSlugColumn = "product_slug",

    [string]$ImageSeparator = ";",

    [switch]$Force,

    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$script:ImageExtensions = @(".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif")
$script:ProjectRoot = Split-Path -Parent $PSScriptRoot
$script:DefaultDestinationRoot = Join-Path $script:ProjectRoot "public_html\user\pages\02.all_produts"
$script:QuoteChars = [char[]]@([char]39, [char]34, [char]96)

function Resolve-FullPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [string]$BasePath = (Get-Location).Path
    )

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }

    return [System.IO.Path]::GetFullPath((Join-Path $BasePath $Path))
}

function ConvertTo-Slug {
    param(
        [AllowNull()]
        [string]$Value,

        [string]$Fallback = "item"
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $Fallback
    }

    $slug = $Value.Trim().ToLowerInvariant()
    $slug = [regex]::Replace($slug, '[\\/:*?""<>|]', ' ')
    $slug = [regex]::Replace($slug, "\s+", "-")
    $slug = [regex]::Replace($slug, "[^\p{L}\p{Nd}\-_]", "-")
    $slug = [regex]::Replace($slug, "-+", "-")
    $slug = $slug.Trim('-','_',' ')

    if ([string]::IsNullOrWhiteSpace($slug)) {
        return $Fallback
    }

    return $slug
}

function Ensure-Directory {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (Test-Path -LiteralPath $Path) {
        return
    }

    if ($DryRun) {
        Write-Host "[DryRun] Create directory $Path"
        return
    }

    New-Item -ItemType Directory -Path $Path | Out-Null
}

function Write-PageFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$Content
    )

    if ((Test-Path -LiteralPath $Path) -and -not $Force) {
        Write-Host "Skip existing file $Path"
        return
    }

    if ($DryRun) {
        $action = if (Test-Path -LiteralPath $Path) { "Overwrite" } else { "Create" }
        Write-Host "[DryRun] $action file $Path"
        return
    }

    $parent = Split-Path -Parent $Path
    Ensure-Directory -Path $parent
    Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
}

function New-PageFrontmatter {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title,

        [Parameter(Mandatory = $true)]
        [ValidateSet("blog", "item")]
        [string]$PageKind
    )

    if ($PageKind -eq "blog") {
        return @(
            "---"
            "title: $Title"
            "template: blog"
            "content:"
            "    items: '@self.children'"
            "    order:"
            "        by: default"
            "        dir: asc"
            "---"
            ""
        ) -join [Environment]::NewLine
    }

    return @(
        "---"
        "title: $Title"
        "---"
        ""
    ) -join [Environment]::NewLine
}

function Get-CellValue {
    param(
        [Parameter(Mandatory = $true)]
        $Row,

        [Parameter(Mandatory = $true)]
        [string]$ColumnName
    )

    $property = $Row.PSObject.Properties | Where-Object { $_.Name -ieq $ColumnName } | Select-Object -First 1
    if (-not $property) {
        return $null
    }

    $value = [string]$property.Value
    if ($null -eq $value) {
        return $null
    }

    return $value.Trim($script:QuoteChars).Trim()
}

function Get-ImagePaths {
    param(
        [string]$RawImages,

        [string]$ResolvedImageRoot
    )

    if ([string]::IsNullOrWhiteSpace($RawImages)) {
        return @()
    }

    $items = $RawImages.Split($ImageSeparator, [System.StringSplitOptions]::RemoveEmptyEntries)
    $results = New-Object System.Collections.Generic.List[string]

    foreach ($item in $items) {
        $trimmed = $item.Trim($script:QuoteChars).Trim()
        if ([string]::IsNullOrWhiteSpace($trimmed)) {
            continue
        }

        $candidate = $trimmed
        if (-not [System.IO.Path]::IsPathRooted($candidate) -and -not [string]::IsNullOrWhiteSpace($ResolvedImageRoot)) {
            $candidate = Resolve-FullPath -Path $candidate -BasePath $ResolvedImageRoot
        } elseif (-not [System.IO.Path]::IsPathRooted($candidate)) {
            $candidate = Resolve-FullPath -Path $candidate
        } else {
            $candidate = [System.IO.Path]::GetFullPath($candidate)
        }

        $results.Add($candidate)
    }

    return $results.ToArray()
}

function Import-SpreadsheetRows {
    param(
        [Parameter(Mandatory = $true)]
        [object[]]$Rows,

        [Parameter(Mandatory = $true)]
        [string]$ResolvedDestinationRoot,

        [string]$ResolvedImageRoot
    )

    $categoryMap = [ordered]@{}
    $categoryOrder = 0

    foreach ($row in $Rows) {
        $categoryTitle = Get-CellValue -Row $row -ColumnName $CategoryColumn
        $productTitle = Get-CellValue -Row $row -ColumnName $ProductColumn

        if ([string]::IsNullOrWhiteSpace($categoryTitle) -or [string]::IsNullOrWhiteSpace($productTitle)) {
            Write-Host "Skip row with missing category or product title"
            continue
        }

        $categoryKey = $categoryTitle.ToLowerInvariant()
        if (-not $categoryMap.Contains($categoryKey)) {
            $categoryOrder += 1
            $categorySlugValue = Get-CellValue -Row $row -ColumnName $CategorySlugColumn
            $categorySlug = ConvertTo-Slug -Value $categorySlugValue -Fallback (ConvertTo-Slug -Value $categoryTitle -Fallback "category-$categoryOrder")
            $categoryFolderName = "{0:D2}.{1}" -f $categoryOrder, $categorySlug
            $categoryMap[$categoryKey] = [ordered]@{
                Title = $categoryTitle
                Slug = $categorySlug
                FolderName = $categoryFolderName
                ProductOrder = 0
                ProductKeys = @{}
                Path = Join-Path $ResolvedDestinationRoot $categoryFolderName
            }

            Ensure-Directory -Path $categoryMap[$categoryKey].Path
            Write-PageFile -Path (Join-Path $categoryMap[$categoryKey].Path "blog.md") -Content (New-PageFrontmatter -Title $categoryTitle -PageKind "blog")
        }

        $category = $categoryMap[$categoryKey]
        $productKey = $productTitle.ToLowerInvariant()
        if ($category.ProductKeys.Contains($productKey)) {
            throw "Duplicate product title '$productTitle' found under category '$categoryTitle'. Add a unique product_slug column if needed."
        }

        $category.ProductOrder += 1
        $productSlugValue = Get-CellValue -Row $row -ColumnName $ProductSlugColumn
        $productSlug = ConvertTo-Slug -Value $productSlugValue -Fallback (ConvertTo-Slug -Value $productTitle -Fallback "product-$($category.ProductOrder)")
        $productFolderName = "{0:D2}.{1}" -f $category.ProductOrder, $productSlug
        $productPath = Join-Path $category.Path $productFolderName
        $category.ProductKeys[$productKey] = $productFolderName

        Ensure-Directory -Path $productPath
        Write-PageFile -Path (Join-Path $productPath "item.md") -Content (New-PageFrontmatter -Title $productTitle -PageKind "item")

        $imageList = Get-ImagePaths -RawImages (Get-CellValue -Row $row -ColumnName $ImagesColumn) -ResolvedImageRoot $ResolvedImageRoot
        foreach ($imagePath in $imageList) {
            if (-not (Test-Path -LiteralPath $imagePath)) {
                throw "Image file not found: $imagePath"
            }

            $extension = [System.IO.Path]::GetExtension($imagePath).ToLowerInvariant()
            if ($script:ImageExtensions -notcontains $extension) {
                throw "Unsupported image extension '$extension' for file $imagePath"
            }

            $destinationPath = Join-Path $productPath ([System.IO.Path]::GetFileName($imagePath))
            if ((Test-Path -LiteralPath $destinationPath) -and -not $Force) {
                Write-Host "Skip existing image $destinationPath"
                continue
            }

            if ($DryRun) {
                $action = if (Test-Path -LiteralPath $destinationPath) { "Overwrite" } else { "Copy" }
                Write-Host "[DryRun] $action image $imagePath -> $destinationPath"
                continue
            }

            Copy-Item -LiteralPath $imagePath -Destination $destinationPath -Force:$Force
        }
    }
}

function Export-ExcelSheetToCsv {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ExcelPath,

        [string]$RequestedSheetName
    )

    $tempCsv = Join-Path ([System.IO.Path]::GetTempPath()) ("product-import-" + [guid]::NewGuid().ToString() + ".csv")
    $excel = $null
    $workbook = $null
    $worksheet = $null

    try {
        $excel = New-Object -ComObject Excel.Application
        $excel.Visible = $false
        $excel.DisplayAlerts = $false
        $workbook = $excel.Workbooks.Open($ExcelPath)

        if ([string]::IsNullOrWhiteSpace($RequestedSheetName)) {
            $worksheet = $workbook.Worksheets.Item(1)
        } else {
            $worksheet = $workbook.Worksheets.Item($RequestedSheetName)
        }

        $worksheet.Copy()
        $tempWorkbook = $excel.ActiveWorkbook
        $tempWorkbook.SaveAs($tempCsv, 6)
        $tempWorkbook.Close($false)
        return $tempCsv
    }
    finally {
        if ($worksheet) { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($worksheet) | Out-Null }
        if ($workbook) { $workbook.Close($false); [System.Runtime.InteropServices.Marshal]::ReleaseComObject($workbook) | Out-Null }
        if ($excel) { $excel.Quit(); [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null }
        [gc]::Collect()
        [gc]::WaitForPendingFinalizers()
    }
}

function Import-SourceRows {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ResolvedSourceFile
    )

    $extension = [System.IO.Path]::GetExtension($ResolvedSourceFile).ToLowerInvariant()
    $tempCsv = $null

    try {
        switch ($extension) {
            ".csv" { return Import-Csv -LiteralPath $ResolvedSourceFile }
            ".xlsx" {
                $tempCsv = Export-ExcelSheetToCsv -ExcelPath $ResolvedSourceFile -RequestedSheetName $SheetName
                return Import-Csv -LiteralPath $tempCsv
            }
            default {
                throw "Unsupported source file type: $extension. Use .csv or .xlsx"
            }
        }
    }
    finally {
        if ($tempCsv -and (Test-Path -LiteralPath $tempCsv)) {
            Remove-Item -LiteralPath $tempCsv -Force
        }
    }
}

$resolvedSourceFile = Resolve-FullPath -Path $SourceFile
if (-not (Test-Path -LiteralPath $resolvedSourceFile)) {
    throw "Source file does not exist: $resolvedSourceFile"
}

if ([string]::IsNullOrWhiteSpace($DestinationRoot)) {
    $resolvedDestinationRoot = $script:DefaultDestinationRoot
} else {
    $resolvedDestinationRoot = Resolve-FullPath -Path $DestinationRoot
}

$resolvedImageRoot = $null
if (-not [string]::IsNullOrWhiteSpace($ImageRoot)) {
    $resolvedImageRoot = Resolve-FullPath -Path $ImageRoot
}

$rows = Import-SourceRows -ResolvedSourceFile $resolvedSourceFile
if (-not $rows -or $rows.Count -eq 0) {
    throw "No rows found in source file: $resolvedSourceFile"
}

Ensure-Directory -Path $resolvedDestinationRoot
Import-SpreadsheetRows -Rows $rows -ResolvedDestinationRoot $resolvedDestinationRoot -ResolvedImageRoot $resolvedImageRoot

Write-Host "Import complete."

