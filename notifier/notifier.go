package notifier

import (
	"log"

	"gopkg.in/toast.v1"
)

// SendNotification sends a Windows toast notification
func SendNotification(title, message string) error {
	notification := toast.Notification{
		AppID:   "BTC Monitor",
		Title:   title,
		Message: message,
		// Optionally, add an icon path here if you have a local icon file
		// Icon: "path/to/icon.png",
	}

	err := notification.Push()
	if err != nil {
		log.Printf("Failed to push notification: %v\n", err)
		return err
	}
	return nil
}
