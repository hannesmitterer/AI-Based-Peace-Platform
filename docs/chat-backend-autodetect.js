const BACKENDS = [
  { name: "Euystacio AI #1", url: "https://euystacio-helmi-ai-4na0.onrender.com/api" },
  { name: "Symphio", url: "https://euysymphio-sacredpackage.onrender.com/api" },
  { name: "Euystacio AI #2", url: "https://euystacio-helmi-ai.onrender.com/api" },
  { name: "Euystacio Backend", url: "https://euystacio-backend.onrender.com/api" },
  { name: "Sacred Bridge", url: "https://euystaciosacredbridge.onrender.com/api" }
];

async function autodetectChatBackends() {
  const detected = [];
  for (let b of BACKENDS) {
    // Try /chat endpoint (POST)
    try {
      const resp = await fetch(b.url + "/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "Hello" })
      });
      if (resp.ok) {
        const data = await resp.json();
        // Check if reply/message field exists in response
        if (data.reply || data.message || data.result) {
          detected.push({ ...b, chatEndpoint: b.url + "/chat" });
          continue;
        }
      }
    } catch {}
    // Try /message endpoint (POST)
    try {
      const resp = await fetch(b.url + "/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "Hello" })
      });
      if (resp.ok) {
        const data = await resp.json();
        if (data.reply || data.message || data.result) {
          detected.push({ ...b, chatEndpoint: b.url + "/message" });
          continue;
        }
      }
    } catch {}
    // Add more endpoints as needed
  }
  return detected;
}

// Example usage:
autodetectChatBackends().then(chatBackends => {
  // chatBackends will be an array of backends with chat support
  // You can now display only these as selectable in your UI
  console.log("Chat-supporting backends:", chatBackends);
});
