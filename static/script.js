document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const form = document.getElementById('config-form');
    const priceDisplay = document.getElementById('current-price');
    const inputPrice = document.getElementById('price');
    const inputInterval = document.getElementById('interval');
    const saveBtnText = document.querySelector('#save-btn span');
    const spinner = document.getElementById('spinner');
    const toast = document.getElementById('toast-message');

    // Polling Interval
    let fetchingIntervalId = null;

    // Load initial config
    async function loadConfig() {
        try {
            const res = await fetch('/api/config');
            if (!res.ok) throw new Error("Failed to config");
            const data = await res.json();

            inputPrice.value = data.price;
            inputInterval.value = data.interval;
            if (data.direction === "greater") {
                document.getElementById('dir-greater').checked = true;
            } else {
                document.getElementById('dir-less').checked = true;
            }
        } catch (error) {
            console.error("Error loading config:", error);
        }
    }

    // Fetch dynamic price
    async function fetchPriceStatus() {
        try {
            const res = await fetch('/api/status');
            if (res.ok) {
                const data = await res.json();
                if (data.current_price > 0) {
                    // format nicely
                    priceDisplay.textContent = `$${data.current_price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                } else {
                    priceDisplay.textContent = "Updating...";
                }
            }
        } catch (error) {
            console.error("Error fetching status:", error);
        }
    }

    // Handle form submit
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const price = parseFloat(inputPrice.value);
        const interval = parseInt(inputInterval.value, 10);
        const direction = document.querySelector('input[name="direction"]:checked').value;

        // UI Feedback
        saveBtnText.textContent = "保存中...";
        spinner.classList.remove('hidden');

        try {
            const res = await fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ price, interval, direction })
            });

            if (res.ok) {
                showToast();
            } else {
                alert("保存失败，请检查输入。");
            }
        } catch (error) {
            console.error(error);
            alert("请求错误。");
        } finally {
            saveBtnText.textContent = "保存配置此生效";
            spinner.classList.add('hidden');
        }
    });

    function showToast() {
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    // Initial load
    loadConfig();
    fetchPriceStatus();
    fetchingIntervalId = setInterval(fetchPriceStatus, 5000); // refresh every 5 seconds locally
});
