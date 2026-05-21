// SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

package cmd

import (
	"log"
	"os"

	"github.com/spf13/cobra"
)

var logger = log.New(os.Stdout, "[launcher] ", log.LstdFlags)

var rootCmd = &cobra.Command{
	Use:   "jobs-launcher",
	Short: "Jobs Launcher supervises subprocesses and handles setup tasks",
}

// Execute runs the root command
func Execute() {
	if err := rootCmd.Execute(); err != nil {
		logger.Printf("Command execution failed: %v", err)
		os.Exit(1)
	}
}
