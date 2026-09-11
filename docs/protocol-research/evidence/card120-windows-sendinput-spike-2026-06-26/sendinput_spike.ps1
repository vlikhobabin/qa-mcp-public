<#
  card 120 spike — prove Win32 SendInput drives the 1C GDI TestClient where the protocol cannot.
  This is the cheap de-risk for the Go host-agent: PowerShell Add-Type P/Invoke calls the IDENTICAL
  user32!SendInput (KEYEVENTF_UNICODE) the Go agent will call via x/sys/windows.

  Usage (run IN interactive session 1, with a 1C create-form open and the Наименование field clicked):
    powershell -ExecutionPolicy Bypass -File sendinput_spike.ps1 -Value "QA SendInput Тест 2026" -Commit

  What it does:
    1. find the 1cv8 client window, SetForegroundWindow (refocus after the console stole focus)
    2. screenshot BEFORE  -> %TEMP%\qa_spike_before.png
    3. SendInput the Unicode -Value into the focused field
    4. if -Commit: Tab (blur -> form-object commit) then Ctrl+S (save -> DB)
    5. screenshot AFTER   -> %TEMP%\qa_spike_after.png
    6. print a JSON result line (QA_SPIKE_RESULT { ... })
  Verify persistence by reopening the item / reading it back; the AFTER png is the visual proof.
#>
param(
  [string]$Value = "QA SendInput Тест 2026",
  [switch]$Commit,
  [int]$FocusSettleMs = 700,
  [int]$CharDelayMs = 12,
  [string]$OutDir = $env:TEMP
)

Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class W {
  [StructLayout(LayoutKind.Sequential)]
  public struct MOUSEINPUT { public int dx; public int dy; public uint mouseData; public uint dwFlags; public uint time; public IntPtr dwExtraInfo; }
  [StructLayout(LayoutKind.Sequential)]
  public struct KEYBDINPUT { public ushort wVk; public ushort wScan; public uint dwFlags; public uint time; public IntPtr dwExtraInfo; }
  [StructLayout(LayoutKind.Explicit)]
  public struct INPUTUNION { [FieldOffset(0)] public MOUSEINPUT mi; [FieldOffset(0)] public KEYBDINPUT ki; }
  [StructLayout(LayoutKind.Sequential)]
  public struct INPUT { public uint type; public INPUTUNION u; }
  const uint INPUT_KEYBOARD = 1;
  const uint KEYEVENTF_KEYUP = 0x0002;
  const uint KEYEVENTF_UNICODE = 0x0004;
  [DllImport("user32.dll", SetLastError=true)] static extern uint SendInput(uint n, INPUT[] p, int cb);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }

  static INPUT Key(ushort vk, ushort scan, uint flags) {
    INPUT i = new INPUT(); i.type = INPUT_KEYBOARD;
    i.u.ki.wVk = vk; i.u.ki.wScan = scan; i.u.ki.dwFlags = flags; return i;
  }
  // genuine Unicode keystroke (KEYEVENTF_UNICODE) — the Cyrillic-safe path, exactly what the Go agent uses
  public static void TypeUnicode(string s, int delayMs) {
    foreach (char c in s) {
      INPUT[] dn = { Key(0, c, KEYEVENTF_UNICODE) };
      INPUT[] up = { Key(0, c, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP) };
      SendInput(1, dn, Marshal.SizeOf(typeof(INPUT)));
      SendInput(1, up, Marshal.SizeOf(typeof(INPUT)));
      System.Threading.Thread.Sleep(delayMs);
    }
  }
  public static void Tap(ushort vk) {
    INPUT[] dn = { Key(vk, 0, 0) }; INPUT[] up = { Key(vk, 0, KEYEVENTF_KEYUP) };
    SendInput(1, dn, Marshal.SizeOf(typeof(INPUT))); System.Threading.Thread.Sleep(40);
    SendInput(1, up, Marshal.SizeOf(typeof(INPUT)));
  }
  public static void Chord(ushort mod, ushort vk) {
    INPUT[] a = { Key(mod, 0, 0) };           SendInput(1, a, Marshal.SizeOf(typeof(INPUT)));
    INPUT[] b = { Key(vk, 0, 0) };            SendInput(1, b, Marshal.SizeOf(typeof(INPUT)));
    System.Threading.Thread.Sleep(40);
    INPUT[] c = { Key(vk, 0, KEYEVENTF_KEYUP) };  SendInput(1, c, Marshal.SizeOf(typeof(INPUT)));
    INPUT[] d = { Key(mod, 0, KEYEVENTF_KEYUP) }; SendInput(1, d, Marshal.SizeOf(typeof(INPUT)));
  }
}
"@

function Shot([string]$path, [W+RECT]$r) {
  $w = [Math]::Max(1, $r.Right - $r.Left); $h = [Math]::Max(1, $r.Bottom - $r.Top)
  $bmp = New-Object System.Drawing.Bitmap $w, $h
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($r.Left, $r.Top, 0, 0, (New-Object System.Drawing.Size $w, $h))
  $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
}

$VK_TAB = 0x09; $VK_RETURN = 0x0D; $VK_CONTROL = 0x11; $VK_S = 0x53

# locate the 1cv8 client window
$proc = Get-Process 1cv8 -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $proc) { Write-Output 'QA_SPIKE_RESULT {"ok":false,"error":"no 1cv8 window with a main handle — is the TestClient up with a form open?"}'; exit 2 }
$h = $proc.MainWindowHandle

[W]::ShowWindow($h, 9) | Out-Null        # SW_RESTORE
[W]::SetForegroundWindow($h) | Out-Null
Start-Sleep -Milliseconds $FocusSettleMs

$r = New-Object W+RECT
[W]::GetWindowRect($h, [ref]$r) | Out-Null

$before = Join-Path $OutDir 'qa_spike_before.png'
$after  = Join-Path $OutDir 'qa_spike_after.png'
Shot $before $r

[W]::TypeUnicode($Value, $CharDelayMs)
Start-Sleep -Milliseconds 300

$didCommit = $false
if ($Commit) {
  [W]::Tap($VK_TAB)            # blur -> object-attribute commit on the form object
  Start-Sleep -Milliseconds 300
  [W]::Chord($VK_CONTROL, $VK_S)   # save -> DB write
  Start-Sleep -Milliseconds 1200
  $didCommit = $true
}

Shot $after $r

$res = @{ ok=$true; value=$Value; committed=$didCommit; window_handle=[int64]$h
         window_title=$proc.MainWindowTitle; rect=@($r.Left,$r.Top,$r.Right,$r.Bottom)
         before=$before; after=$after } | ConvertTo-Json -Compress
Write-Output ("QA_SPIKE_RESULT " + $res)
