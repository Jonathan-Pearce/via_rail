/**
 * Format an ISO date string (YYYY-MM-DD) to a short display label (e.g., "Apr 1").
 */
export function formatShortDate(isoDate: string): string {
  try {
    const [year, month, day] = isoDate.split('-').map(Number);
    const d = new Date(year, month - 1, day);
    return d.toLocaleDateString('en-CA', { month: 'short', day: 'numeric' });
  } catch {
    return isoDate;
  }
}

/**
 * Format an ISO date string to a long display label (e.g., "April 1, 2025 EST").
 */
export function formatLongDate(isoDate: string): string {
  try {
    const [year, month, day] = isoDate.split('-').map(Number);
    const d = new Date(year, month - 1, day);
    return d.toLocaleDateString('en-CA', { year: 'numeric', month: 'long', day: 'numeric' });
  } catch {
    return isoDate;
  }
}

/**
 * Format a number as a percentage with one decimal place.
 */
export function formatPct(val: number | null | undefined): string {
  if (val == null) return '—';
  return `${val.toFixed(1)}%`;
}

/**
 * Format delay minutes to a human-readable string.
 */
export function formatDelay(val: number | null | undefined): string {
  if (val == null) return '—';
  if (val < 0) return `${Math.abs(val).toFixed(1)} min early`;
  if (val === 0) return 'On time';
  return `${val.toFixed(1)} min`;
}
