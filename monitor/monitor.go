package monitor

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"

	"btc_monitor/notifier"
)

// Config represents the user configuration
type Config struct {
	Price     float64 `json:"price"`
	Interval  int     `json:"interval"`  // in minutes
	Direction string  `json:"direction"` // "greater" or "less"
}

// AppConfig is the global configuration state thread-safe
type AppConfig struct {
	sync.RWMutex
	Conf Config
}

// Global configurations and state
var (
	GlobalConfig = &AppConfig{
		Conf: Config{
			Price:     65900.0,
			Interval:  5,
			Direction: "greater",
		},
	}
	CurrentPrice float64
	priceMutex   sync.RWMutex

	// to prevent repeating alerts when the price stays beyond target
	alreadyAlerted bool
	alertMutex     sync.Mutex

	// Control channel for the monitor loop to allow restarting on config changes
	resetChan = make(chan struct{})
)

// UpdateConfig updates the current config and signals the monitor loop to restart
func UpdateConfig(newConf Config) {
	GlobalConfig.Lock()
	GlobalConfig.Conf = newConf
	GlobalConfig.Unlock()

	// Reset alert state when config changes
	alertMutex.Lock()
	alreadyAlerted = false
	alertMutex.Unlock()

	// Signal the monitor loop to restart its timer
	select {
	case resetChan <- struct{}{}:
	default:
	}
}

func GetConfig() Config {
	GlobalConfig.RLock()
	defer GlobalConfig.RUnlock()
	return GlobalConfig.Conf
}

func GetCurrentPrice() float64 {
	priceMutex.RLock()
	defer priceMutex.RUnlock()
	return CurrentPrice
}

func setPrice(p float64) {
	priceMutex.Lock()
	defer priceMutex.Unlock()
	CurrentPrice = p
}

// fetchBinancePrice calls Binance API to get BTCUSDT price
func fetchBinancePrice() (float64, error) {
	resp, err := http.Get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
	if err != nil {
		return 0, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return 0, fmt.Errorf("binance API returned status: %d", resp.StatusCode)
	}

	var data struct {
		Price string `json:"price"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&data); err != nil {
		return 0, err
	}

	var price float64
	_, err = fmt.Sscanf(data.Price, "%f", &price)
	if err != nil {
		return 0, err
	}

	return price, nil
}

func checkPriceAndAlert() {
	price, err := fetchBinancePrice()
	if err != nil {
		log.Printf("Error fetching price: %v", err)
		return
	}
	setPrice(price)
	log.Printf("Current BTC Price: $%.2f", price)

	conf := GetConfig()
	triggered := false
	if conf.Direction == "greater" {
		triggered = price >= conf.Price
	} else {
		triggered = price <= conf.Price
	}

	alertMutex.Lock()
	defer alertMutex.Unlock()

	if triggered {
		if !alreadyAlerted {
			alreadyAlerted = true
			dirStr := "≥"
			if conf.Direction == "less" {
				dirStr = "≤"
			}
			msg := fmt.Sprintf("当前价格: $%.2f %s 设定的 $%.2f", price, dirStr, conf.Price)
			log.Printf("Alert triggered! %s", msg)
			notifier.SendNotification("BTC 价格提醒", msg)
		}
	} else {
		alreadyAlerted = false
	}
}

// StartMonitorLoop starts the background polling loop
func StartMonitorLoop() {
	// Execute an initial check right away
	checkPriceAndAlert()

	for {
		conf := GetConfig()
		interval := time.Duration(conf.Interval) * time.Minute
		if interval <= 0 {
			interval = 5 * time.Minute
		}

		timer := time.NewTimer(interval)

		select {
		case <-timer.C:
			checkPriceAndAlert()
		case <-resetChan:
			// Config was updated, stop current timer and restart loop
			if !timer.Stop() {
				// drain channel if timer already fired but we didn't receive from it yet
				select {
				case <-timer.C:
				default:
				}
			}
			log.Println("Config updated, restarting monitor timer...")
			checkPriceAndAlert() // run a check immediately on config update
		}
	}
}
