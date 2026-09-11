//go:build windows

package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"os/exec"
	"time"

	"golang.org/x/sys/windows"
)

type hiddenPromptS5WindowsResponse struct {
	OK          bool                    `json:"ok"`
	Code        string                  `json:"code"`
	Focused     bool                    `json:"focused"`
	PatternHash string                  `json:"pattern_hash"`
	MatchCount  int                     `json:"match_count"`
	Controls    []hiddenPromptS5Control `json:"controls"`
}

var hiddenPromptS5PostMessage = windows.NewLazySystemDLL("user32.dll").NewProc("PostMessageW")

func runHiddenPromptS5PowerShell(script string, response *hiddenPromptS5WindowsResponse) error {
	powershell, err := exec.LookPath("powershell.exe")
	if err != nil {
		return errors.New("hidden prompt UIA runtime is unavailable")
	}
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
	defer cancel()
	command := exec.CommandContext(ctx, powershell, "-NoProfile", "-NonInteractive", "-EncodedCommand", hiddenDirectEncodedCommand(script))
	hideChildWindow(command)
	configureProcessGroup(command)
	output, commandErr := command.Output()
	if ctx.Err() != nil || commandErr != nil || !json.Valid(output) || json.Unmarshal(output, response) != nil || !response.OK {
		return fmt.Errorf("hidden prompt UIA operation failed: %s", response.Code)
	}
	return nil
}

func observeHiddenPromptS5Controls(prompt hiddenWindowIdentity) (string, []hiddenPromptS5Control, hiddenPromptS5InventoryDiagnostic, error) {
	if prompt.HWND == 0 || prompt.PID == 0 || prompt.ClassName != hiddenPromptS5Class {
		return "", nil, hiddenPromptS5InventoryDiagnostic{}, errors.New("exact hidden prompt identity is invalid")
	}
	var response hiddenPromptS5WindowsResponse
	operationErr := runHiddenPromptS5PowerShell(fmt.Sprintf(hiddenPromptS5InventoryScript, prompt.HWND), &response)
	diagnostic := hiddenPromptS5InventoryDiagnostic{Code: response.Code, Complete: response.OK,
		HashesValid: validHiddenWindowHash(response.PatternHash), RowCount: len(response.Controls)}
	buttonHash := hiddenWindowHash("ControlType.Button")
	for _, row := range response.Controls {
		if row.PID == prompt.PID {
			diagnostic.ExactPIDCount++
		}
		if row.ControlTypeHash == buttonHash && row.PathHash == hiddenPromptS5ActionPathHash && row.Bottom && row.HorizontalRank == 0 && row.HorizontalPeerCount == 2 {
			diagnostic.TargetMatchCount++
		}
		diagnostic.HashesValid = diagnostic.HashesValid && validHiddenWindowHash(row.ControlTypeHash) && validHiddenWindowHash(row.PathHash) &&
			validHiddenWindowHash(row.GeometryHash) && validHiddenWindowHash(row.RootGeometryHash)
	}
	if operationErr != nil || validateHiddenPromptS5InventoryDiagnostic(diagnostic) != nil || len(response.Controls) == 0 {
		return "", nil, diagnostic, errors.New("hidden prompt inventory is invalid")
	}
	return response.PatternHash, response.Controls, diagnostic, nil
}

func confirmHiddenPromptS5Windows(hwnd uintptr, action hiddenPromptS5Control) (bool, uint64, error) {
	if hwnd == 0 || action.PID == 0 ||
		!validHiddenWindowHash(action.PathHash) || !validHiddenWindowHash(action.GeometryHash) || !validHiddenWindowHash(action.RootGeometryHash) {
		return false, 0, errors.New("exact hidden prompt action identity is invalid")
	}
	var response hiddenPromptS5WindowsResponse
	script := fmt.Sprintf(hiddenPromptS5FocusScript, hwnd, action.RootGeometryHash, action.PID, action.PathHash, action.GeometryHash)
	if err := runHiddenPromptS5PowerShell(script, &response); err != nil || !response.Focused || response.MatchCount != 1 {
		return false, 0, errors.New("exact hidden prompt focus failed")
	}
	for _, message := range [][3]uintptr{{0x0100, 0x0d, 0x001c0001}, {0x0101, 0x0d, 0xc01c0001}} {
		if ok, _, _ := hiddenPromptS5PostMessage.Call(hwnd, message[0], message[1], message[2]); ok == 0 {
			return true, 0, errors.New("addressed hidden prompt message failed")
		}
	}
	return true, 2, nil
}

const hiddenPromptS5InventoryScript = `$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue';[Console]::OutputEncoding=[Text.Encoding]::UTF8
function Hash-S5([string]$v){$s=[Security.Cryptography.SHA256]::Create();try{return([BitConverter]::ToString($s.ComputeHash([Text.Encoding]::UTF8.GetBytes($v)))).Replace('-','').ToLowerInvariant()}finally{$s.Dispose()}}
function O([bool]$ok,[string]$code,[string]$ph,$c){[Console]::Out.Write(([pscustomobject]@{ok=$ok;code=$code;pattern_hash=$ph;controls=@($c)}|ConvertTo-Json -Depth 5 -Compress));exit 0}
try{Add-Type -AssemblyName UIAutomationClient;Add-Type -AssemblyName UIAutomationTypes;$r=[Windows.Automation.AutomationElement]::FromHandle([IntPtr]%d)}catch{O $false 'root_failed' '' @()};if($null-eq$r){O $false 'root_missing' '' @()}
$rr=$r.Current.BoundingRectangle;if($rr.Width-le0-or$rr.Height-le0){O $false 'geometry_missing' '' @()};$rg=Hash-S5('{0},{1},{2},{3}'-f[int]$rr.X,[int]$rr.Y,[int]$rr.Width,[int]$rr.Height);$w=[Windows.Automation.TreeWalker]::ControlViewWalker
$e=@($r);try{$d=$r.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)}catch{O $false 'enumeration_failed' '' @()};foreach($x in $d){$e+=$x};if($e.Count-gt128){O $false 'control_limit_exceeded' '' @()};$rows=@();$pr=@();$n=0
foreach($x in $e){try{$p=$null;$i=$x.TryGetCurrentPattern([Windows.Automation.InvokePattern]::Pattern,[ref]$p);$p=$null;$v=$x.TryGetCurrentPattern([Windows.Automation.ValuePattern]::Pattern,[ref]$p);$ro=$v-and$p.Current.IsReadOnly;$p=$null;$ec=$x.TryGetCurrentPattern([Windows.Automation.ExpandCollapsePattern]::Pattern,[ref]$p);$p=$null;$si=$x.TryGetCurrentPattern([Windows.Automation.SelectionItemPattern]::Pattern,[ref]$p);$ps=@();if($i){$ps+='InvokePattern'};if($v){$ps+='ValuePattern'};if($ec){$ps+='ExpandCollapsePattern'};if($si){$ps+='SelectionItemPattern'};$ct=$x.Current.ControlType.ProgrammaticName;$ch=Hash-S5($x.Current.ClassName);$ah=Hash-S5($x.Current.AutomationId);$pr+=($ct+'|'+$ch+'|'+$ah+'|'+$x.Current.IsEnabled.ToString().ToLowerInvariant()+'|'+$ro.ToString().ToLowerInvariant()+'|'+$x.Current.IsOffscreen.ToString().ToLowerInvariant()+'|'+(($ps|Sort-Object)-join','));$q=$x.Current.BoundingRectangle;$g=Hash-S5('{0},{1},{2},{3}'-f[int]$q.X,[int]$q.Y,[int]$q.Width,[int]$q.Height);$path=@();$z=$x;for($j=0;$j-lt64-and$null-ne$z;$j++){$path+=($z.Current.ControlType.ProgrammaticName+'|'+(Hash-S5 $z.Current.ClassName)+'|'+(Hash-S5 $z.Current.AutomationId));$z=$w.GetParent($z)};$ph=Hash-S5($path-join'>');$bottom=$q.Width-gt0-and$q.Height-gt0-and(($q.Y+$q.Height/2-$rr.Y)/$rr.Height)-ge.75;$rows+=[pscustomobject]@{pid=$x.Current.ProcessId;control_type_hash=Hash-S5($ct);path_hash=$ph;geometry_hash=$g;root_geometry_hash=$rg;enabled=$x.Current.IsEnabled;read_only=$ro;offscreen=$x.Current.IsOffscreen;invoke=$i;value=$v;bottom=$bottom;x=[double]$q.X;n=$n};$n++}catch{try{if($x.Current.ControlType-eq[Windows.Automation.ControlType]::Button){O $false 'row_failed' '' @()}}catch{O $false 'row_failed' '' @()}}}
$out=@();foreach($a in $rows){$peers=@($rows|Where-Object{$_.control_type_hash-eq(Hash-S5 'ControlType.Button')-and$_.path_hash-eq$a.path_hash-and$_.enabled-and-not$_.offscreen-and$_.invoke-and$_.bottom}|Sort-Object x,n);$rank=-1;for($j=0;$j-lt$peers.Count;$j++){if($peers[$j].n-eq$a.n){$rank=$j}};$out+=[pscustomobject]@{PID=$a.pid;ControlTypeHash=$a.control_type_hash;PathHash=$a.path_hash;GeometryHash=$a.geometry_hash;RootGeometryHash=$a.root_geometry_hash;Enabled=$a.enabled;ReadOnly=$a.read_only;Offscreen=$a.offscreen;Invoke=$a.invoke;Value=$a.value;Bottom=$a.bottom;HorizontalRank=$rank;HorizontalPeerCount=$peers.Count}}
O $true 'observed' (Hash-S5(($pr|Sort-Object)-join([char]10))) $out`

const hiddenPromptS5FocusScript = `$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue';[Console]::OutputEncoding=[Text.Encoding]::UTF8
function Hash-S5([string]$v){$s=[Security.Cryptography.SHA256]::Create();try{return([BitConverter]::ToString($s.ComputeHash([Text.Encoding]::UTF8.GetBytes($v)))).Replace('-','').ToLowerInvariant()}finally{$s.Dispose()}};function O([bool]$ok,[int]$count,[bool]$focused){[Console]::Out.Write(([pscustomobject]@{ok=$ok;match_count=$count;focused=$focused}|ConvertTo-Json -Compress));exit 0}
try{Add-Type -AssemblyName UIAutomationClient;Add-Type -AssemblyName UIAutomationTypes;$r=[Windows.Automation.AutomationElement]::FromHandle([IntPtr]%d)}catch{O $false 0 $false};if($null-eq$r){O $false 0 $false};$rr=$r.Current.BoundingRectangle;if((Hash-S5('{0},{1},{2},{3}'-f[int]$rr.X,[int]$rr.Y,[int]$rr.Width,[int]$rr.Height))-ne'%s'){O $false 0 $false};$w=[Windows.Automation.TreeWalker]::ControlViewWalker;$m=@();$buttonCondition=[Windows.Automation.PropertyCondition]::new([Windows.Automation.AutomationElement]::ControlTypeProperty,[Windows.Automation.ControlType]::Button);$d=$r.FindAll([Windows.Automation.TreeScope]::Descendants,$buttonCondition)
foreach($x in $d){try{$p=$null;if($x.Current.ProcessId-ne%d-or-not$x.Current.IsEnabled-or$x.Current.IsOffscreen-or-not$x.TryGetCurrentPattern([Windows.Automation.InvokePattern]::Pattern,[ref]$p)){continue};$path=@();$z=$x;for($j=0;$j-lt64-and$null-ne$z;$j++){$path+=($z.Current.ControlType.ProgrammaticName+'|'+(Hash-S5 $z.Current.ClassName)+'|'+(Hash-S5 $z.Current.AutomationId));$z=$w.GetParent($z)};$q=$x.Current.BoundingRectangle;if((Hash-S5($path-join'>'))-eq'%s'-and(Hash-S5('{0},{1},{2},{3}'-f[int]$q.X,[int]$q.Y,[int]$q.Width,[int]$q.Height))-eq'%s'){$m+=$x}}catch{O $false 0 $false}}
if($m.Count-ne1){O $false $m.Count $false};try{$m[0].SetFocus();$limit=[DateTime]::UtcNow.AddSeconds(2);while(-not$m[0].Current.HasKeyboardFocus-and[DateTime]::UtcNow-lt$limit){Start-Sleep -Milliseconds 50};O $m[0].Current.HasKeyboardFocus 1 $m[0].Current.HasKeyboardFocus}catch{O $false 1 $false}`
