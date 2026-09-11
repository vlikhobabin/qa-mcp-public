package main

import "strings"

func windowsCommandLine(executable string, args []string) string {
	parts := make([]string, 0, len(args)+1)
	parts = append(parts, windowsQuoteArg(executable))
	for _, arg := range args {
		parts = append(parts, windowsQuoteArg(arg))
	}
	return strings.Join(parts, " ")
}

func windowsArgumentLine(args []string) string {
	parts := make([]string, 0, len(args))
	for _, arg := range args {
		parts = append(parts, windowsQuoteArg(arg))
	}
	return strings.Join(parts, " ")
}

// testClientShellArgumentLine renders the one-string command line expected by
// 1C when Windows Shell owns process creation. 1C's connection, username and
// password tokens use doubled embedded quotes; the C-runtime backslash quoting
// used by CreateProcess is not equivalent after ShellExecute reparses vArgs.
func testClientShellArgumentLine(args []string) string {
	parts := make([]string, 0, len(args))
	for index := 0; index < len(args); index++ {
		arg := args[index]
		switch {
		case strings.EqualFold(arg, "/IBConnectionString") && index+1 < len(args):
			index++
			parts = append(parts, arg+" "+testClientShellQuote(args[index]))
		case strings.HasPrefix(strings.ToUpper(arg), "/N"):
			parts = append(parts, arg[:2]+testClientShellQuote(arg[2:]))
		case strings.HasPrefix(strings.ToUpper(arg), "/P"):
			parts = append(parts, arg[:2]+testClientShellQuote(arg[2:]))
		default:
			parts = append(parts, arg)
		}
	}
	return strings.Join(parts, " ")
}

func testClientShellQuote(value string) string {
	return `"` + strings.ReplaceAll(value, `"`, `""`) + `"`
}

func windowsQuoteArg(arg string) string {
	if arg == "" {
		return `""`
	}
	if !strings.ContainsAny(arg, " \t\n\v\"") {
		return arg
	}
	var out strings.Builder
	out.WriteByte('"')
	backslashes := 0
	for _, r := range arg {
		if r == '\\' {
			backslashes++
			continue
		}
		if r == '"' {
			out.WriteString(strings.Repeat(`\`, backslashes*2+1))
			out.WriteRune(r)
			backslashes = 0
			continue
		}
		if backslashes > 0 {
			out.WriteString(strings.Repeat(`\`, backslashes))
			backslashes = 0
		}
		out.WriteRune(r)
	}
	if backslashes > 0 {
		out.WriteString(strings.Repeat(`\`, backslashes*2))
	}
	out.WriteByte('"')
	return out.String()
}
