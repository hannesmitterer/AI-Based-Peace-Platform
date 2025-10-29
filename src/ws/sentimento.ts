import { IncomingMessage } from 'http';
import { WebSocket, WebSocketServer } from 'ws';
import { Server as HTTPServer } from 'http';
import { SentimentoLiveEvent } from '../types/sentimento';
import { seed003Metrics } from '../metrics/seed003';

/**
 * SentimentoWSHub manages WebSocket connections for live sentiment broadcasts
 * Implements backpressure control and feeds Seed-003 KPI metrics
 */
export class SentimentoWSHub {
  private wss: WebSocketServer;
  private clients: Set<WebSocket> = new Set();
  private bufferMaxKB: number;

  constructor(server: HTTPServer, bufferMaxKB: number = 512) {
    this.bufferMaxKB = bufferMaxKB;
    this.wss = new WebSocketServer({ noServer: true });

    // Attach to HTTP server upgrade event
    server.on('upgrade', (request: IncomingMessage, socket, head) => {
      const pathname = new URL(request.url || '', `http://${request.headers.host}`).pathname;

      if (pathname === '/api/v2/sentimento/live') {
        this.wss.handleUpgrade(request, socket, head, (ws) => {
          this.wss.emit('connection', ws, request);
        });
      }
    });

    // Handle new WebSocket connections
    this.wss.on('connection', (ws: WebSocket) => {
      this.handleConnection(ws);
    });
  }

  /**
   * Handle new WebSocket connection
   */
  private handleConnection(ws: WebSocket): void {
    this.clients.add(ws);
    console.log(`[SentimentoWSHub] New client connected. Total clients: ${this.clients.size}`);

    // Send welcome message
    const welcome = {
      type: 'welcome',
      message: 'Connected to Sentimento Live feed',
      timestamp: new Date().toISOString(),
    };
    this.sendToClient(ws, welcome);

    // Handle client disconnect
    ws.on('close', () => {
      this.clients.delete(ws);
      console.log(`[SentimentoWSHub] Client disconnected. Total clients: ${this.clients.size}`);
    });

    // Handle errors
    ws.on('error', (error) => {
      console.error('[SentimentoWSHub] WebSocket error:', error);
      this.clients.delete(ws);
    });

    // Handle incoming messages (optional - currently we only broadcast)
    ws.on('message', (data) => {
      console.log('[SentimentoWSHub] Received message from client:', data.toString());
    });
  }

  /**
   * Send data to a single client with backpressure control
   */
  private sendToClient(ws: WebSocket, data: any): boolean {
    if (ws.readyState !== WebSocket.OPEN) {
      return false;
    }

    // Check backpressure - drop send if buffer is too large
    const bufferSize = ws.bufferedAmount;
    const maxBytes = this.bufferMaxKB * 1024;

    if (bufferSize > maxBytes) {
      console.warn(`[SentimentoWSHub] Dropping send - buffer size ${bufferSize} exceeds max ${maxBytes}`);
      return false;
    }

    try {
      ws.send(JSON.stringify(data));
      return true;
    } catch (error) {
      console.error('[SentimentoWSHub] Error sending to client:', error);
      return false;
    }
  }

  /**
   * Broadcast a SentimentoLiveEvent to all connected clients
   * Also feeds the event to Seed-003 KPI metrics
   */
  broadcast(event: SentimentoLiveEvent): void {
    // Feed to Seed-003 metrics
    seed003Metrics.pushSample(event.composites.sorrow, event.composites.hope);

    // Broadcast to all clients
    let successCount = 0;
    let failCount = 0;

    this.clients.forEach((client) => {
      if (this.sendToClient(client, event)) {
        successCount++;
      } else {
        failCount++;
      }
    });

    console.log(
      `[SentimentoWSHub] Broadcast complete - Success: ${successCount}, Failed: ${failCount}`
    );
  }

  /**
   * Get current connection count
   */
  getClientCount(): number {
    return this.clients.size;
  }

  /**
   * Close all connections and shutdown
   */
  shutdown(): void {
    console.log('[SentimentoWSHub] Shutting down...');
    this.clients.forEach((client) => {
      client.close(1000, 'Server shutdown');
    });
    this.wss.close();
  }
}
