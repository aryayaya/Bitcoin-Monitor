package web

import (
	"net/http"

	"btc_monitor/monitor"

	"github.com/gin-gonic/gin"
)

func SetupRouter() *gin.Engine {
	// gin.SetMode(gin.ReleaseMode)
	r := gin.Default()

	// Serve static files (HTML, CSS, JS)
	r.Static("/static", "./static")
	r.StaticFile("/", "./static/index.html")

	api := r.Group("/api")
	{
		api.GET("/config", getConfig)
		api.POST("/config", updateConfig)
		api.GET("/status", getStatus)
	}

	return r
}

func getConfig(c *gin.Context) {
	c.JSON(http.StatusOK, monitor.GetConfig())
}

func updateConfig(c *gin.Context) {
	var req monitor.Config
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if req.Price <= 0 || req.Interval <= 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid price or interval"})
		return
	}

	if req.Direction != "greater" && req.Direction != "less" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Direction must be 'greater' or 'less'"})
		return
	}

	monitor.UpdateConfig(req)
	c.JSON(http.StatusOK, gin.H{"message": "Config updated successfully"})
}

func getStatus(c *gin.Context) {
	price := monitor.GetCurrentPrice()
	c.JSON(http.StatusOK, gin.H{
		"current_price": price,
	})
}
