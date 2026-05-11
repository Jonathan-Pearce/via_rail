/* ─────────────────────────────────────────────────────────────────────────
   Shared HTTP client — thin wrapper over fetch
   ───────────────────────────────────────────────────────────────────────── */

const BASE_URL = import.meta.env.VITE_API_BASE ?? ''

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export async function apiFetch<T>(
  path: string,
  params?: Record<string, string | number | boolean | null | undefined>,
): Promise<T> {
  const url = new URL(BASE_URL + path, window.location.origin)
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== null && value !== undefined && value !== '') {
        url.searchParams.set(key, String(value))
      }
    }
  }

  const res = await fetch(url.toString(), {
    headers: { Accept: 'application/json' },
  })

  if (!res.ok) {
    let message = `HTTP ${res.status}`
    try {
      const body = await res.json()
      message = body?.detail ?? message
    } catch {
      /* use default */
    }
    throw new ApiError(res.status, message)
  }

  return res.json() as Promise<T>
}
