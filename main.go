package main

import (
	"fmt"
	"log"
	"os/exec"
	"runtime"
	"time"

	"btc_monitor/monitor"
	"btc_monitor/web"
)

func openBrowser(url string) {
	var err error

	switch runtime.GOOS {
	case "linux":
		err = exec.Command("xdg-open", url).Start()
	case "windows":
		err = exec.Command("rundll32", "url.dll,FileProtocolHandler", url).Start()
	case "darwin":
		err = exec.Command("open", url).Start()
	default:
		err = fmt.Errorf("unsupported platform")
	}
	if err != nil {
		log.Printf("Failed to open browser: %v", err)
	}
}

func main() {
	// 1. Start monitor loop in a separate goroutine
	go monitor.StartMonitorLoop()

	// 2. Start the web server
	router := web.SetupRouter()

	port := ":8080"
	log.Printf("Starting web server on http://localhost%s", port)

	// Automatically open the browser after a short delay
	go func() {
		time.Sleep(1 * time.Second)
		openBrowser("http://localhost" + port)
	}()

	err := router.Run(port)
	if err != nil {
		log.Fatalf("Failed to run web server: %v", err)
	}
}
