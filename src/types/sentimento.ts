/**
 * Canonical type for Sentimento Live events broadcasted via WebSocket.
 * Represents real-time emotional composites (hope, sorrow) with timestamp.
 */
export interface SentimentoLiveEvent {
  /**
   * ISO 8601 timestamp of when the event was generated
   */
  timestamp: string;

  /**
   * Composite emotional metrics
   */
  composites: {
    /**
     * Hope metric (0.0 - 1.0)
     */
    hope: number;

    /**
     * Sorrow metric (0.0 - 1.0)
     */
    sorrow: number;
  };

  /**
   * Event sequence number for ordering
   */
  sequence?: number;
}
