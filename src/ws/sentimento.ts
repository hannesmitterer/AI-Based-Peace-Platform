import { Server as HTTPServer } from 'http';
import { WebSocketServer, WebSocket } from 'ws';
import { SentimentoLiveEvent } from '../types/sentimento';

/**
 * Seed-003 metrics aggregator for Sentimento events
 */
class Seed003Metrics {
  private samples: Array<{ sorrow: number; hope: number; timestamp: number }> = [];
  private readonly maxSamples = 1000;

  pushSample(sorrow: number, hope: number): void {
    this.samples.push({
      sorrow,
      hope,
      timestamp: Date.now()
    });

    // Keep only recent samples
    if (this.samples.length > this.maxSamples) {
      this.samples.shift();
    }
  }

  getHopeRatio(): number {
    if (this.samples.length === 0) return 0;
    
    const totalHope = this.samples.reduce((sum, s) => sum + s.hope, 0);
    const totalSorrow = this.samples.reduce((sum, s) => sum + s.sorrow, 0);
    const total = totalHope + totalSorrow;
    
    return total > 0 ? totalHope / total : 0;
  }
}

/**
 * WebSocket hub for Sentimento Live events.
 * Manages client connections, applies backpressure, and broadcasts events.
 */
export class SentimentoWSHub {
  private wss: WebSocketServer;
  private clients: Set<WebSocket> = new Set();
  private sequence: number = 0;
  private metrics: Seed003Metrics = new Seed003Metrics();
  
  // Configuration from environment
  private readonly bufferMaxKB: number;

  constructor() {
    this.bufferMaxKB = parseInt(process.env.SENTIMENTO_BUFFER_MAX_KB || '512', 10);
    
    this.wss = new WebSocketServer({ noServer: true });
    this.wss.on('connection', this.handleConnection.bind(this));
  }

  /**
   * Attach to HTTP server upgrade event on /api/v2/sentimento/live
   */
  attach(server: HTTPServer): void {
    server.on('upgrade', (request, socket, head) => {
      if (request.url === '/api/v2/sentimento/live') {
        this.wss.handleUpgrade(request, socket, head, (ws) => {
          this.wss.emit('connection', ws, request);
        });
      }
    });
  }

  private handleConnection(ws: WebSocket): void {
    this.clients.add(ws);
    console.log(`[SentimentoWSHub] Client connected. Total clients: ${this.clients.size}`);

    ws.on('close', () => {
      this.clients.delete(ws);
      console.log(`[SentimentoWSHub] Client disconnected. Total clients: ${this.clients.size}`);
    });

    ws.on('error', (error) => {
      console.error('[SentimentoWSHub] WebSocket error:', error);
      this.clients.delete(ws);
    });
  }

  /**
   * Broadcast a Sentimento event to all connected clients with backpressure handling
   */
  broadcast(event: Omit<SentimentoLiveEvent, 'sequence'>): void {
    // Add sequence number
    const fullEvent: SentimentoLiveEvent = {
      ...event,
      sequence: this.sequence++
    };

    // Push to Seed-003 metrics
    this.metrics.pushSample(event.composites.sorrow, event.composites.hope);

    const message = JSON.stringify(fullEvent);
    const maxBufferBytes = this.bufferMaxKB * 1024;

    // Broadcast to all clients with backpressure drop
    this.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        // Check backpressure: if buffered amount exceeds limit, drop message
        if (client.bufferedAmount > maxBufferBytes) {
          console.warn('[SentimentoWSHub] Dropping message for client due to backpressure');
          return;
        }

        try {
          client.send(message);
        } catch (error) {
          console.error('[SentimentoWSHub] Error sending message:', error);
        }
      }
    });
  }

  /**
   * Get the current hope ratio from Seed-003 metrics
   */
  getHopeRatio(): number {
    return this.metrics.getHopeRatio();
  }

  /**
   * Close all connections and shut down the hub
   */
  close(): void {
    this.clients.forEach((client) => {
      client.close();
    });
    this.wss.close();
  }
}
