/**
 * Seed-003: Hope Transduction Layer (ARSP-001)
 * Rolling buffer for hope/sorrow KPI tracking
 */

interface Sample {
  sorrow: number;
  hope: number;
  timestamp: number;
}

class HopeKpiBuffer {
  private samples: Sample[] = [];
  private windowSec: number;

  constructor(windowSec: number = 120) {
    this.windowSec = windowSec;
  }

  /**
   * Push a new sample (sorrow, hope) into the rolling buffer
   * @param sorrow - Sorrow value [0,1]
   * @param hope - Hope value [0,1]
   */
  pushSample(sorrow: number, hope: number): void {
    // Validate inputs
    if (sorrow < 0 || sorrow > 1 || hope < 0 || hope > 1) {
      throw new Error('Sorrow and hope values must be in range [0,1]');
    }

    const now = Date.now();
    this.samples.push({ sorrow, hope, timestamp: now });

    // Remove samples outside the rolling window
    const cutoff = now - this.windowSec * 1000;
    this.samples = this.samples.filter(s => s.timestamp > cutoff);
  }

  /**
   * Get rolling KPI metrics
   * @returns Object with avgSorrow, avgHope, ratio, samples count, and window duration
   */
  getRollingKpi(): {
    avgSorrow: number;
    avgHope: number;
    ratio: number;
    samples: number;
    windowSec: number;
  } {
    // Clean up old samples first
    const now = Date.now();
    const cutoff = now - this.windowSec * 1000;
    this.samples = this.samples.filter(s => s.timestamp > cutoff);

    if (this.samples.length === 0) {
      return {
        avgSorrow: 0,
        avgHope: 0,
        ratio: 0,
        samples: 0,
        windowSec: this.windowSec,
      };
    }

    const totalSorrow = this.samples.reduce((sum, s) => sum + s.sorrow, 0);
    const totalHope = this.samples.reduce((sum, s) => sum + s.hope, 0);
    
    const avgSorrow = totalSorrow / this.samples.length;
    const avgHope = totalHope / this.samples.length;
    
    // Calculate ratio: hope/(sorrow+hope) to get a normalized metric
    // If both are 0, ratio is 0.5 (neutral)
    let ratio = 0.5;
    if (avgSorrow + avgHope > 0) {
      ratio = avgHope / (avgSorrow + avgHope);
    }

    return {
      avgSorrow: Math.round(avgSorrow * 1000) / 1000,
      avgHope: Math.round(avgHope * 1000) / 1000,
      ratio: Math.round(ratio * 1000) / 1000,
      samples: this.samples.length,
      windowSec: this.windowSec,
    };
  }
}

// Global singleton instance
const globalBuffer = new HopeKpiBuffer(
  parseInt(process.env.SEED003_ROLLING_WINDOW_SEC || '120', 10)
);

export function pushSample(sorrow: number, hope: number): void {
  globalBuffer.pushSample(sorrow, hope);
}

export function getRollingKpi() {
  return globalBuffer.getRollingKpi();
}
