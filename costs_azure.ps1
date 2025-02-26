function Connect-AzureIfNeeded {
    param (
        [string]$SubscriptionName
    )

    # Check if the user is already connected to Azure
    $connected = $true
    try {
        # Try a command that requires authentication
        Get-AzResourceGroup -ErrorAction Stop | Out-Null
    }
    catch {
        $connected = false
    }

    if (-not $connected) {
        Write-Host "Not connected to Azure. Logging in..."

        # Login to Azure and select the subscription with the name "foo"
        Connect-AzAccount
        $subscription = Get-AzSubscription | Where-Object { $_.Name -eq "foo" }

        if ($subscription) {
            Set-AzContext -Subscription $subscription.Id
            Write-Host "Logged in and switched to subscription: foo"
        } else {
            Write-Host "Subscription 'foo' not found."
        }
    } else {
        Write-Host "Already connected to Azure."
        $currentSubscription = Get-AzContext | Select-Object -ExpandProperty Subscription
        Write-Host "Current subscription: $($currentSubscription.Name)"

        # Check if the current subscription is 'foo'
        if ($currentSubscription.Name -ne $SubscriptionName) {
            Write-Host "Switching to subscription: $SubscriptionName..."
            $subscription = Get-AzSubscription | Where-Object { $_.Name -eq $SubscriptionName }

            if ($subscription) {
                Set-AzContext -Subscription $subscription.Id
                Write-Host "Switched to subscription: $SubscriptionName"
            } else {
                Write-Host "Subscription '$SubscriptionName' not found."
            }
        }
    }
}

Write-Output ""
Connect-AzureIfNeeded -SubscriptionName "ccaas-dev-dev_labs"

# Set the time range for cost analysis (last 30 days)
$startDate = (Get-Date).AddDays(-30).ToString("yyyy-MM-dd")
$endDate = Get-Date -Format "yyyy-MM-dd"

# print new line and print start date and end date of usage
Write-Output ""
Write-Output "Azure Cost for the period: $startDate to $endDate"
Write-Output ""

# Get all resource groups with the specified tags
$resourceGroups = Get-AzResourceGroup | Where-Object {
    $_.Tags.Owner -eq "dkirrane" -and $_.Tags.Team -eq "Platform"
}

# Initialize total cost
$totalCost = 0

# Loop through each resource group and get its cost
foreach ($rg in $resourceGroups) {
    $usage = Get-AzConsumptionUsageDetail -StartDate $startDate -EndDate $endDate -ResourceGroup $rg.ResourceGroupName

    # Write-Output "Resource Group: $($rg.ResourceGroupName), Usage: $($usage.Count)"

    # if usage count > 0, then calculate the cost
    if ($usage.Count -gt 0) {
        $cost = $usage | Measure-Object -Property PretaxCost -Sum | Select-Object -ExpandProperty Sum
        $totalCost += $cost
        Write-Output ("{0,-40} {1,-40}" -f $rg.ResourceGroupName, $cost.ToString('F2'))
    } else {
        Write-Output ("{0,-40} {1,-40}" -f $rg.ResourceGroupName, "No usage data found")
    }
}

Write-Output ""
Write-Output ("{0,-40} {1,-40}" -f "TOTAL COST:", $($totalCost.ToString('F2')))
Write-Output ""