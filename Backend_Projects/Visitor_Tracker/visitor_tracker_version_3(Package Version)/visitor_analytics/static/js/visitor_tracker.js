/**
 * Hybrid Visitor Telemetry & Device Verification Engine
 */
async function detectDeviceAndBrowser() {
    const ua = navigator.userAgent;
    let detectedBrowser = "Unknown Browser";
    let detectedOS = "Unknown OS";
    let detectedDevice = "Desktop";

    // 1. RESOLVE OPERATING SYSTEM
    if (/Android/i.test(ua)) {
        detectedOS = "Android";
    } else if (/iPhone|iPad|iPod/i.test(ua)) {
        detectedOS = /iPad/i.test(ua) ? "iPadOS" : "iOS";
    } else if (/Mac/i.test(ua)) {
        detectedOS = (navigator.maxTouchPoints && navigator.maxTouchPoints > 1) ? "iPadOS" : "macOS";
    } else if (/Linux/i.test(ua)) {
        detectedOS = "Linux";
    } else if (/Win/i.test(ua)) {
        detectedOS = "Windows";
    }

    // 2. DISAMBIGUATE TOUCH LAPTOPS VS MOBILES
    const isMobileUA = /Android|webOS|iPhone|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua);
    const isTabletUA = /iPad/i.test(ua) || (detectedOS === "iPadOS");
    const isSmallScreen = window.innerWidth <= 768;

    if (isTabletUA) {
        detectedDevice = "Tablet";
    } else if (isMobileUA) {
        detectedDevice = "Mobile";
    } else if (navigator.userAgentData && navigator.userAgentData.mobile) {
        detectedDevice = "Mobile";
    } else if ((detectedOS === "Windows" || detectedOS === "macOS" || detectedOS === "Linux") && isSmallScreen) {
        detectedDevice = "Mobile (Desktop Mode)";
    } else {
        detectedDevice = "Desktop";
    }

    // 3. BRAVE DETECTION
    if (navigator.brave && await navigator.brave.isBrave()) {
        detectedBrowser = "Brave Browser";
    }
    // 4. MICROSOFT EDGE
    else if (ua.includes("Edg/") || (navigator.userAgentData && navigator.userAgentData.brands && navigator.userAgentData.brands.some(b => b.brand.includes("Microsoft Edge")))) {
        detectedBrowser = "Microsoft Edge";
    }
    // 5. OPERA
    else if (ua.includes("OPR/") || ua.includes("Opera/") || window.opr) {
        detectedBrowser = "Opera";
    }
    // 6. VIVALDI
    else if (ua.includes("Vivaldi/")) {
        detectedBrowser = "Vivaldi";
    }
    // 7. MOZILLA FIREFOX
    else if (ua.includes("Firefox/") && !ua.includes("Seamonkey/")) {
        detectedBrowser = "Mozilla Firefox";
    }
    // 8. APPLE SAFARI
    else if (ua.includes("Safari/") && !ua.includes("Chrome/") && !ua.includes("Chromium/")) {
        detectedBrowser = "Apple Safari";
    }
    // 9. GENUINE GOOGLE CHROME
    else if (ua.includes("Chrome/") && !ua.includes("Chromium/")) {
        detectedBrowser = "Google Chrome";
    }

    // 10. WINDOWS 11 HIGH-ENTROPY CHECK
    if (detectedOS === "Windows" && navigator.userAgentData && navigator.userAgentData.getHighEntropyValues) {
        try {
            const hints = await navigator.userAgentData.getHighEntropyValues(["platformVersion", "platform"]);
            if (hints.platform === "Windows") {
                const majorVersion = parseInt(hints.platformVersion.split('.')[0]);
                detectedOS = majorVersion >= 13 ? "Windows 11" : "Windows 10";
            }
        } catch(e) {}
    }

    // Send payload to Django API
    fetch('/visitor-analytics/verify-browser/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        browser: detectedBrowser,
        os: detectedOS,
        device: detectedDevice
    })
});
}

// Execute automatically when DOM is fully loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', detectDeviceAndBrowser);
} else {
    detectDeviceAndBrowser();
}