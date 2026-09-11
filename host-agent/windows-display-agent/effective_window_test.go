package main

import "testing"

func TestEffectiveWindow(t *testing.T) {
	cases := []struct {
		name       string
		window     string
		clientPort int
		want       string
	}{
		{"explicit title wins over port", "Бухгалтерия предприятия, редакция 3.0", 15383, "Бухгалтерия предприятия, редакция 3.0"},
		{"explicit selector wins over port", "class:V8TopLevelFrame", 15383, "class:V8TopLevelFrame"},
		{"blank window falls back to client port", "", 15383, "port:15383"},
		{"whitespace window falls back to client port", "   ", 15382, "port:15382"},
		{"wildcard window falls back to client port", "*", 15382, "port:15382"},
		{"no window and no port stays blank", "", 0, ""},
		{"no window and negative port stays blank", "", -1, ""},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			if got := effectiveWindow(tc.window, tc.clientPort); got != tc.want {
				t.Fatalf("effectiveWindow(%q,%d) = %q, want %q", tc.window, tc.clientPort, got, tc.want)
			}
		})
	}
}
