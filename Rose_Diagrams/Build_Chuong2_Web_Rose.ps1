[CmdletBinding()]
param(
    [string] $OutputPath = (Join-Path $PSScriptRoot 'RentalSystem_Chuong2_Web.mdl'),
    [string] $PreviewDirectory
)

$ErrorActionPreference = 'Stop'
$OutputPath = [IO.Path]::GetFullPath($OutputPath)
if ([IO.Path]::GetExtension($OutputPath) -ine '.mdl' -or (Test-Path -LiteralPath $OutputPath)) {
    throw 'Choose a new output path with the .mdl extension.'
}

$content = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'Chuong2_Web_Rose.json') -Raw -Encoding UTF8 |
    ConvertFrom-Json -AsHashtable

function Invoke-Rose($Object, [string] $Member, [string] $Operation, [object[]] $Arguments = @()) {
    if ($null -eq $Object) { throw "Missing Rose object when calling $Member." }
    try {
        $value = $Object.GetType().InvokeMember($Member, [Reflection.BindingFlags]$Operation,
            $null, $Object, $Arguments)
        if ($null -ne $value) { return ,$value }
    } catch {
        throw "Rose $Operation $Member failed: $($_.Exception.GetBaseException().Message)"
    }
}
function Get-Rose($Object, $Member) { Invoke-Rose $Object $Member GetProperty }
function Set-Rose($Object, $Member, $Value) { Invoke-Rose $Object $Member SetProperty @($Value) }
function Call-Rose($Object, $Member, [object[]] $Arguments = @()) {
    Invoke-Rose $Object $Member InvokeMethod $Arguments
}

function Set-Position($View, [int] $X, [int] $Y) {
    Set-Rose $View XPosition ([int16]$X)
    Set-Rose $View YPosition ([int16]$Y)
}
function Set-Size($View, [int] $Width, [int] $Height) {
    Set-Rose $View Width ([int16]$Width)
    Set-Rose $View Height ([int16]$Height)
}
function Set-FontSize($View, [int] $Size) {
    $font = Get-Rose $View Font
    if ($font) { Set-Rose $font Size ([int16]$Size) }
}
function Get-FigureTitle([int] $Number, [string] $Label) {
    'Hinh 2.{0:00} - {1}' -f $Number, $Label
}

$rose = New-Object -ComObject Rose.Application
$model = Get-Rose $rose CurrentModel
if ((Call-Rose $model IsModified) -or (Call-Rose $model GetFileName)) {
    throw 'Rose Automation opened an existing or modified model. Start with an empty automation model.'
}

$useRoot = Get-Rose $model RootUseCaseCategory
$logicRoot = Get-Rose $model RootCategory
$system = Call-Rose $useRoot AddCategory @('02.3 RentalSystem Web')
$business = Call-Rose $useRoot AddCategory @('02.2 Nghiep vu thue thiet bi')
$analysis = Call-Rose $logicRoot AddCategory @('02.4 Lop phan tich Web')
$figures = @{}

$actors = @{}
foreach ($id in $content.actors.Keys) {
    $actor = Call-Rose $system AddClass @($content.actors[$id])
    Set-Rose $actor Stereotype 'actor'
    $actors[$id] = $actor
}

$systemCases = @{}
foreach ($spec in $content.cases) {
    $id, $name, $participants, $description = $spec
    $useCase = Call-Rose $system AddUseCase @("UC-$id $name")
    Set-Rose $useCase Documentation $description
    $systemCases[$id] = @{ item = $useCase; actors = $participants }
}
$businessCases = @{}
foreach ($spec in $content.business) {
    $id, $name, $participants = $spec
    $businessCases[$id] = @{
        item = (Call-Rose $business AddUseCase @("NV-$id $name"))
        actors = $participants
    }
}

$associations = @{}
foreach ($group in @($businessCases, $systemCases)) {
    foreach ($entry in $group.Values) {
        $useCase = $entry.item
        $target = Call-Rose $useCase GetQualifiedName
        foreach ($id in $entry.actors) {
            $key = "$id/$target"
            $associations[$key] = Call-Rose $actors[$id] AddAssociation @('', $target)
        }
    }
}

function New-UseCaseFigure($Package, [int] $Number, $Name, $Cases, [string[]] $Ids) {
    $diagram = Call-Rose $Package AddUseCaseDiagram @((Get-FigureTitle $Number $Name))
    $usedActors = [Collections.Generic.HashSet[string]]::new()
    foreach ($id in $Ids) {
        foreach ($actorId in $Cases[$id].actors) { $null = $usedActors.Add($actorId) }
    }

    $columns = if ($Ids.Count -gt 8) { 2 } else { 1 }
    $rows = [int][Math]::Ceiling($Ids.Count / [double]$columns)
    $rowGap = 610
    $actorY = @{ KH=780; TT=([Math]::Max(1450,$rows*$rowGap-120)); KD=770; QT=1500; KT=2230 }
    foreach ($actorId in $content.actors.Keys) {
        if (!$usedActors.Contains($actorId)) { continue }
        $actor = $actors[$actorId]
        if (!(Call-Rose $diagram AddClass @($actor))) { throw "Unable to add actor $actorId." }
        $actorView = Call-Rose $diagram GetClassView @($actor)
        $x = if ($actorId -in 'KH','TT') { 560 } elseif ($columns -eq 2) { 7630 } else { 5980 }
        Set-Position $actorView $x $actorY[$actorId]
    }

    for ($index=0; $index -lt $Ids.Count; $index++) {
        $entry = $Cases[$Ids[$index]]
        if (!(Call-Rose $diagram AddUseCase @($entry.item))) {
            throw "Unable to add a use case in figure $Number."
        }
        $view = Call-Rose $diagram GetViewFrom @($entry.item)
        $x = if ($columns -eq 1) { 3250 } elseif ($index -lt $rows) { 2730 } else { 5450 }
        Set-Position $view $x (520 + ($index % $rows)*$rowGap)
        Set-Size $view 2260 480
    }

    foreach ($id in $Ids) {
        $entry = $Cases[$id]
        $target = Call-Rose $entry.item GetQualifiedName
        foreach ($actorId in $entry.actors) {
            if (!(Call-Rose $diagram AddAssociation @($associations["$actorId/$target"]))) {
                throw "Unable to display association $actorId to $target."
            }
        }
    }
    return ,$diagram
}

$figures[1] = New-UseCaseFigure $business 1 'Ca su dung nghiep vu tong quat' $businessCases @('1','2','3','4','5','6','7')
foreach ($group in $content.groups) {
    $number, $name, $ids = $group
    $figures[[int]$number] = New-UseCaseFigure $system $number $name $systemCases $ids
}

$workflow = Call-Rose $business AddCategory @('Bay quy trinh Web')
$scenarioActors = @{}
foreach ($flow in $content.flows) {
    $owner = Call-Rose $workflow AddUseCase @($flow.title)
    Set-Rose $owner Documentation "$($flow.ucs). $($flow.notes)"
    $null = Call-Rose $owner CreateStateMachine
    $stateMachines = Get-Rose (Get-Rose $owner StateMachineOwner) StateMachines
    $machine = Call-Rose $stateMachines GetAt @([int16]1)
    $activity = Call-Rose $machine AddActivityDiagram @((Get-FigureTitle $flow.first "Hoat dong - $($flow.title)"))
    Set-Rose $activity Documentation $flow.notes

    $laneWidth = 4070
    $maxRow = ($flow.nodes | ForEach-Object { [int]$_.row } | Measure-Object -Maximum).Maximum
    $laneHeight = 940 + 500*$maxRow
    for ($i=0; $i -lt $flow.lanes.Count; $i++) {
        $lane = Call-Rose $machine AddSwimLane @($flow.lanes[$i])
        $laneView = Call-Rose $activity AddSwimLaneView @($lane)
        Set-Size $laneView $laneWidth $laneHeight
        Set-Position $laneView (150+$laneWidth*$i+[int]($laneWidth/2)) (200+[int]($laneHeight/2))
    }

    $nodes = @{}
    foreach ($item in $flow.nodes) {
        switch ($item.kind) {
            'activity' { $node = Call-Rose $machine AddActivity @($item.label); $viewMethod = 'AddActivityView' }
            'decision' { $node = Call-Rose $machine AddDecision @($item.label); $viewMethod = 'AddDecisionView' }
            default {
                $node = Call-Rose $machine AddState @($item.kind)
                $stateKind = if ($item.kind -eq 'start') { 'Initial' } else { 'Final' }
                Set-Rose (Get-Rose $node StateKind) Name $stateKind
                $viewMethod = 'AddStateView'
            }
        }
        $nodes[$item.id] = $node
        $view = Call-Rose $activity $viewMethod @($node)
        $x = 1150 + $item.lane*$laneWidth + 1950*$item.track
        Set-Position $view $x (690+500*$item.row)
        if ($item.kind -eq 'activity') { Set-Size $view 1740 280 }
        if ($item.kind -eq 'decision') { Set-Size $view 300 240 }
    }
    foreach ($edge in $flow.edges) {
        $guard = if ($edge.guard) { "[$($edge.guard)]" } else { '' }
        $transition = Call-Rose $nodes[$edge.from] AddTransitionToVertex @($guard,$nodes[$edge.to])
        $null = Call-Rose $activity AddRelationView @($transition)
        if (!(Call-Rose $activity GetViewFrom @($transition))) {
            throw "Missing transition view $($edge.from) -> $($edge.to) in figure $($flow.first)."
        }
    }
    $figures[[int]$flow.first] = $activity

    foreach ($diagramType in 1,2) {
        $caption = if ($diagramType -eq 1) { 'Tuan tu' } else { 'Cong tac' }
        $number = [int]$flow.first+$diagramType
        $diagram = Call-Rose $owner AddScenarioDiagram @((Get-FigureTitle $number "$caption - $($flow.title)"),[int16]$diagramType)
        Set-Rose $diagram Documentation $flow.notes
        if ((Call-Rose $diagram GetDiagramType) -ne $diagramType) { throw "Wrong interaction type in figure $number." }

        $positions = @{
            user=@(720,720); ui=@(4440,720); ctrl=@(4440,3050); db=@(720,3050); staff=@(8000,720)
        }
        if ($flow.parties.Contains('pay')) {
            $positions.pay = @(720,2750)
            $positions.ctrl = @(4440,2750)
            $positions.db = @(8000,2750)
        }
        $sequenceIds = @('user','ui','pay','staff','ctrl','db') |
            Where-Object { $flow.parties.Contains($_) }
        $participants = @{}
        $partyIndex = 0
        foreach ($id in $sequenceIds) {
            $name = $flow.parties[$id]
            $actorClass = $null
            if ($id -eq 'user' -or $id -eq 'pay' -or $id -eq 'staff') {
                if ($name -eq $content.actors.KH) { $actorClass = $actors.KH }
                elseif ($name -eq $content.actors.TT) { $actorClass = $actors.TT }
                else {
                    if (!$scenarioActors.ContainsKey($name)) {
                        $scenarioActors[$name] = Call-Rose $workflow AddClass @($name)
                        Set-Rose $scenarioActors[$name] Stereotype 'actor'
                    }
                    $actorClass = $scenarioActors[$name]
                }
            }
            $instance = Call-Rose $diagram AddInstance @($name,'')
            if ($actorClass) {
                Set-Rose $instance ClassName (Call-Rose $actorClass GetQualifiedName)
                Set-Rose $instance Name ''
            }
            $participants[$id] = $instance
            $view = Call-Rose $diagram AddInstanceView @($instance,$false)
            if ($diagramType -eq 1) {
                Set-Position $view (790 + 2180*$partyIndex) 650
            } else {
                Set-Position $view $positions[$id][0] $positions[$id][1]
            }
            Set-FontSize $view 10
            $partyIndex++
        }
        $step = 0
        foreach ($item in $flow.messages) {
            $step++
            $message = Call-Rose $diagram CreateMessage @($item.label,
                $participants[$item.from],$participants[$item.to],[int16]$step)
            if (!$message) { throw "Unable to create message $step in figure $number." }
            $view = Call-Rose $diagram GetViewFrom @($message)
            if ($view) { Set-FontSize $view 9 }
        }

        if ((Get-Rose (Call-Rose $diagram GetMessages) Count) -ne $flow.messages.Count) {
            throw "Missing messages in figure $number."
        }
        $figures[$number] = $diagram
    }
}

$classDiagram = Call-Rose $analysis AddClassDiagram @((Get-FigureTitle 27 'Lop muc phan tich RentalSystem Web'))
$classes = @{}
foreach ($spec in $content.classes) {
    $id,$label,$stereotype,$x,$y = $spec
    $class = Call-Rose $analysis AddClass @($label)
    Set-Rose $class Stereotype $stereotype
    if (!(Call-Rose $classDiagram AddClass @($class))) { throw "Unable to display class $label." }
    $view = Call-Rose $classDiagram GetClassView @($class)
    Set-Rose $view SuppressAttributes $true
    Set-Rose $view SuppressOperations $true
    Set-Position $view $x $y
    $classes[$id] = $class
}
foreach ($link in $content.classLinks) {
    $source,$target,$label,$sourceMultiplicity,$targetMultiplicity = $link
    $from = $classes[$source]
    $to = $classes[$target]
    $relation = Call-Rose $from AddAssociation @($label,(Call-Rose $to GetQualifiedName))
    if ($sourceMultiplicity) {
        $sourceRole = Call-Rose $relation GetCorrespondingRole @($from)
        $targetRole = Call-Rose $relation GetCorrespondingRole @($to)
        Set-Rose $sourceRole Cardinality $sourceMultiplicity
        Set-Rose $targetRole Cardinality $targetMultiplicity
    }
    if (!(Call-Rose $classDiagram AddAssociation @($relation))) {
        throw "Unable to display association $source to $target."
    }
}
$figures[27] = $classDiagram

if ($figures.Count -ne 27 -or @(1..27 | Where-Object { !$figures.Contains([int]$_) }).Count) {
    throw 'Expected one native Rose diagram per figure, from 2.01 to 2.27.'
}
$nativeFile = Call-Rose $model SaveAs @($OutputPath)
if (!$nativeFile -or !(Test-Path -LiteralPath $OutputPath)) { throw 'Rose could not save the native model.' }

if ($PreviewDirectory) {
    $preview = [IO.Directory]::CreateDirectory([IO.Path]::GetFullPath($PreviewDirectory))
    foreach ($number in 1..27) {
        $path = Join-Path $preview.FullName ('Hinh_2_{0:00}.emf' -f $number)
        $null = Call-Rose $figures[$number] RenderEnhanced @($path)
    }
}

Write-Output "Saved $($figures.Count) native Rose diagrams to $OutputPath."
