/**
 * Seed-003 KPI tracking module
 * Maintains hope/sorrow ratio metrics for monitoring
 */

interface KPISample {
  timestamp: number;
  hope: number;
  sorrow: number;
}

class Seed003Metrics {
  private samples: KPISample[] = [];
  private readonly maxSamples: number = 1000;

  /**
   * Push a new sentiment sample to the KPI tracker
   * @param sorrow - Sorrow value (0.0 - 1.0)
   * @param hope - Hope value (0.0 - 1.0)
   */
  pushSample(sorrow: number, hope: number): void {
    const sample: KPISample = {
      timestamp: Date.now(),
      hope,
      sorrow,
    };

    this.samples.push(sample);

    // Keep only the most recent samples
    if (this.samples.length > this.maxSamples) {
      this.samples.shift();
    }
  }

  /**
   * Calculate the current hope ratio
   * @returns Hope ratio (hope / (hope + sorrow)) or 0 if both are 0
   */
  getHopeRatio(): number {
    if (this.samples.length === 0) {
      return 0;
    }

    // Calculate average hope and sorrow from recent samples
    const recentSamples = this.samples.slice(-100);
    const avgHope = recentSamples.reduce((sum, s) => sum + s.hope, 0) / recentSamples.length;
    const avgSorrow = recentSamples.reduce((sum, s) => sum + s.sorrow, 0) / recentSamples.length;

    const total = avgHope + avgSorrow;
    if (total === 0) {
      return 0;
    }

    return avgHope / total;
  }

  /**
   * Get recent samples
   * @param count - Number of recent samples to retrieve
   */
  getRecentSamples(count: number = 100): KPISample[] {
    return this.samples.slice(-count);
  }

  /**
   * Get statistics summary
   */
  getStats() {
    if (this.samples.length === 0) {
      return {
        hopeRatio: 0,
        sampleCount: 0,
        avgHope: 0,
        avgSorrow: 0,
      };
    }

    const recentSamples = this.samples.slice(-100);
    const avgHope = recentSamples.reduce((sum, s) => sum + s.hope, 0) / recentSamples.length;
    const avgSorrow = recentSamples.reduce((sum, s) => sum + s.sorrow, 0) / recentSamples.length;

    return {
      hopeRatio: this.getHopeRatio(),
      sampleCount: this.samples.length,
      avgHope,
      avgSorrow,
    };
  }
}

// Export singleton instance
export const seed003Metrics = new Seed003Metrics();
