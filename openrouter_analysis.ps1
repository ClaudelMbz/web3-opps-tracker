# Analyse des modèles gratuits OpenRouter
$json = Get-Content "openrouter_models.json" | ConvertFrom-Json

# Filtrer les modèles gratuits
$freeModels = $json.data | Where-Object { 
    $_.pricing.prompt -eq "0" -and $_.pricing.completion -eq "0" 
}

# Créer un tableau avec les informations importantes
$modelList = @()
foreach ($model in $freeModels) {
    $paramSize = "N/A"
    
    # Extraire la taille des paramètres du nom ou de l'ID
    if ($model.name -match "(\d+)B" -or $model.id -match "(\d+)b") {
        $paramSize = $matches[1] + "B"
    } elseif ($model.name -match "(\d+)M" -or $model.id -match "(\d+)m") {
        $paramSize = $matches[1] + "M"
    }
    
    # Calculer une valeur numérique pour le tri
    $sortValue = 0
    if ($paramSize -match "(\d+)B") {
        $sortValue = [int]$matches[1] * 1000
    } elseif ($paramSize -match "(\d+)M") {
        $sortValue = [int]$matches[1]
    }
    
    $modelInfo = [PSCustomObject]@{
        Name = $model.name
        ID = $model.id
        Parameters = $paramSize
        SortValue = $sortValue
        ContextLength = $model.context_length
        Description = $model.description
    }
    
    $modelList += $modelInfo
}

# Trier par taille des paramètres (plus grand en premier)
$sortedModels = $modelList | Sort-Object SortValue -Descending

Write-Host "=== MODÈLES GRATUITS D'OPENROUTER (CLASSÉS DU MEILLEUR AU MOINS BON) ===" -ForegroundColor Green
Write-Host ""

$rank = 1
foreach ($model in $sortedModels) {
    Write-Host "$rank. $($model.Name)" -ForegroundColor Cyan
    Write-Host "   ID: $($model.ID)" -ForegroundColor Gray
    Write-Host "   Taille: $($model.Parameters) paramètres" -ForegroundColor Yellow
    Write-Host "   Contexte: $($model.ContextLength) tokens" -ForegroundColor Magenta
    
    $desc = $model.Description
    if ($desc.Length -gt 150) {
        $desc = $desc.Substring(0, 150) + "..."
    }
    Write-Host "   Description: $desc" -ForegroundColor White
    Write-Host ""
    
    $rank++
}

Write-Host "=== RÉSUMÉ ===" -ForegroundColor Green
Write-Host "Nombre total de modèles gratuits: $($sortedModels.Count)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Top 5 par taille de paramètres:" -ForegroundColor Green
$top5 = $sortedModels | Where-Object { $_.Parameters -ne "N/A" } | Select-Object -First 5
foreach ($model in $top5) {
    Write-Host "- $($model.Name) ($($model.Parameters))" -ForegroundColor Cyan
}
