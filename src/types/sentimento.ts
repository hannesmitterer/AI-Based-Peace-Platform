/**
 * Canonical SentimentoLiveEvent payload shape
 * Represents real-time sentiment analysis data broadcast via WebSocket
 */
export interface SentimentoLiveEvent {
  /**
   * Timestamp of the event in ISO 8601 format
   */
  timestamp: string;

  /**
   * Composite sentiment values
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
   * Optional metadata about the event
   */
  metadata?: {
    /**
     * Source identifier for the sentiment data
     */
    source?: string;

    /**
     * Geographic region if applicable
     */
    region?: string;

    /**
     * Additional context
     */
    [key: string]: any;
  };
}

/**
 * Ingest payload for POST /ingest/sentimento
 */
export interface SentimentoIngestPayload {
  composites: {
    hope: number;
    sorrow: number;
  };
  metadata?: {
    source?: string;
    region?: string;
    [key: string]: any;
  };
}
