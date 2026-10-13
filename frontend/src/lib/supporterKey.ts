const STORAGE_KEY = 'fi_supporter_key'

function generateKey(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }
  return `anon-${Math.random().toString(36).slice(2)}-${Date.now()}`
}

export function getSupporterKey(): string {
  const existing = localStorage.getItem(STORAGE_KEY)
  if (existing?.trim()) {
    return existing.trim()
  }
  const created = generateKey()
  localStorage.setItem(STORAGE_KEY, created)
  return created
}
