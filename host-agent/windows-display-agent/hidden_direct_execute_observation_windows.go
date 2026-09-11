//go:build windows

package main

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"os/exec"
	"time"
	"unicode/utf16"
)

type hiddenDirectUIAResponse struct {
	OK    bool                 `json:"ok"`
	Code  string               `json:"code"`
	Items []hiddenDirectUIARow `json:"items"`
}

func hiddenDirectEncodedCommand(value string) string {
	units := utf16.Encode([]rune(value))
	bytes := make([]byte, 0, len(units)*2)
	for _, unit := range units {
		bytes = append(bytes, byte(unit), byte(unit>>8))
	}
	return base64.StdEncoding.EncodeToString(bytes)
}

func observeHiddenDirectUIA(hwnd uintptr, pid uint32) ([]hiddenDirectUIARow, error) {
	if hwnd == 0 || pid == 0 {
		return nil, errors.New("exact UIA root identity is invalid")
	}
	powershell, err := exec.LookPath("powershell.exe")
	if err != nil {
		return nil, errors.New("passive UIA runtime is unavailable")
	}
	script := fmt.Sprintf(hiddenDirectPassiveUIAScript, hwnd)
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
	defer cancel()
	command := exec.CommandContext(ctx, powershell, "-NoProfile", "-NonInteractive", "-EncodedCommand", hiddenDirectEncodedCommand(script))
	hideChildWindow(command)
	configureProcessGroup(command)
	output, commandErr := command.Output()
	if ctx.Err() != nil {
		return nil, errors.New("passive UIA observation timed out")
	}
	if commandErr != nil || !json.Valid(output) {
		return nil, errors.New("passive UIA observation failed")
	}
	var response hiddenDirectUIAResponse
	if json.Unmarshal(output, &response) != nil || !response.OK || response.Code != "observed" || len(response.Items) == 0 || len(response.Items) > hiddenDirectUIALimit {
		return nil, errors.New("passive UIA response is invalid")
	}
	paths := make(map[string]struct{}, len(response.Items))
	for _, row := range response.Items {
		if row.PID != pid || !validHiddenWindowHash(row.ControlTypeHash) || !validHiddenWindowHash(row.ClassHash) ||
			!validHiddenWindowHash(row.AutomationIDHash) || !validHiddenWindowHash(row.NameHash) || !validHiddenWindowHash(row.PathHash) {
			return nil, errors.New("passive UIA row is foreign or malformed")
		}
		if _, duplicate := paths[row.PathHash]; duplicate {
			return nil, errors.New("passive UIA topology is ambiguous")
		}
		paths[row.PathHash] = struct{}{}
	}
	return response.Items, nil
}

const hiddenDirectPassiveUIAScript = `
$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue';[Console]::OutputEncoding=[Text.Encoding]::UTF8
function Out-Fixed([bool]$ok,[string]$code,$items){[Console]::Out.Write(([pscustomobject]@{ok=$ok;code=$code;items=@($items)}|ConvertTo-Json -Depth 4 -Compress));exit 0}
function Hash-Value([string]$value){$sha=[Security.Cryptography.SHA256]::Create();try{return ([BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($value)))).Replace('-','').ToLowerInvariant()}finally{$sha.Dispose()}}
try{Add-Type -AssemblyName UIAutomationClient;Add-Type -AssemblyName UIAutomationTypes;$root=[Windows.Automation.AutomationElement]::FromHandle([IntPtr]%d)}catch{Out-Fixed $false 'root_failed' @()}
if($null-eq$root){Out-Fixed $false 'root_missing' @()}
try{$desc=$root.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)}catch{Out-Fixed $false 'enumeration_failed' @()}
if(($desc.Count+1)-gt512){Out-Fixed $false 'inventory_oversized' @()}
$elements=@($root);foreach($element in $desc){$elements+=$element};$rows=@()
foreach($element in $elements){try{
  $runtime=($element.GetRuntimeId() -join ',');$pattern=$null
  $invoke=$element.TryGetCurrentPattern([Windows.Automation.InvokePattern]::Pattern,[ref]$pattern);$pattern=$null
  $value=$element.TryGetCurrentPattern([Windows.Automation.ValuePattern]::Pattern,[ref]$pattern);$pattern=$null
  $expand=$element.TryGetCurrentPattern([Windows.Automation.ExpandCollapsePattern]::Pattern,[ref]$pattern);$pattern=$null
  $select=$element.TryGetCurrentPattern([Windows.Automation.SelectionItemPattern]::Pattern,[ref]$pattern)
  $rows+=[pscustomobject]@{PID=$element.Current.ProcessId;ControlTypeHash=(Hash-Value $element.Current.ControlType.ProgrammaticName);ClassHash=(Hash-Value $element.Current.ClassName);AutomationIDHash=(Hash-Value $element.Current.AutomationId);NameHash=(Hash-Value $element.Current.Name);PathHash=(Hash-Value $runtime);Invoke=$invoke;Value=$value;ExpandCollapse=$expand;SelectionItem=$select}
}catch{Out-Fixed $false 'row_failed' @()}}
Out-Fixed $true 'observed' $rows
`
