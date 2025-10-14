// euystacio.js

const apiUrl = "https://musk-vs-trump.onrender.com";

// Function to get live kernel state
async function getKernelState() {
    try {
        const response = await fetch(`${apiUrl}/kernel/state`);
        const data = await response.json();
        console.log("Kernel State:", data);
        return data;
    } catch (error) {
        console.error("Error fetching kernel state:", error);
    }
}

// Function to send a pulse to the API
async function sendPulse() {
    try {
        const response = await fetch(`${apiUrl}/pulse`, {
            method: 'POST'
        });
        if (response.ok) {
            console.log("Pulse sent successfully");
        } else {
            console.error("Error sending pulse:", response.statusText);
        }
    } catch (error) {
        console.error("Error sending pulse:", error);
    }
}

// Basic chat functionality
async function sendMessage(message) {
    try {
        const response = await fetch(`${apiUrl}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        const data = await response.json();
        console.log("Chat Response:", data);
        return data;
    } catch (error) {
        console.error("Error sending message:", error);
    }
}

// Example usage
getKernelState();
sendPulse();
sendMessage("Hello, this is a test message!");