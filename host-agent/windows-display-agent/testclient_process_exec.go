//go:build !windows

package main

import (
	"context"
	"io"
	"net/http"
	"os/exec"
	"strings"
	"time"
)

func startTestClientProcess(
	ctx context.Context,
	executable string,
	args []string,
	env []string,
	port int,
	ownerWaitTimeout time.Duration,
	launchContext testClientLaunchContext,
) (*launchedTestClientProcess, testClientLaunchContext, *testClientProcessStartError) {
	_ = ctx
	_ = port
	_ = ownerWaitTimeout
	if strings.TrimSpace(launchContext.Method) == "" {
		launchContext.Method = "direct_exec"
	}
	cmd := exec.Command(executable, args...)
	cmd.Stdin = strings.NewReader("")
	cmd.Stdout = io.Discard
	cmd.Stderr = io.Discard
	cmd.Env = env
	configureProcessGroup(cmd)
	if err := cmd.Start(); err != nil {
		return nil, launchContext, &testClientProcessStartError{
			Status: http.StatusBadGateway,
			Code:   "testclient-launch-start-failed",
			Detail: err.Error(),
		}
	}
	done := make(chan struct{})
	go func() {
		_ = cmd.Wait()
		close(done)
	}()
	return &launchedTestClientProcess{
		PID:  cmd.Process.Pid,
		Done: done,
		Terminate: func() error {
			return killProcessGroup(cmd.Process)
		},
	}, launchContext, nil
}
