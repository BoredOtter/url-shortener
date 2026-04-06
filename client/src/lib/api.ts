import { z } from "zod"

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ??
  "/api"

const shortenRequestSchema = z.object({
  url: z.string().url("Enter a valid URL")
})

const shortenResponseSchema = z.object({
  short_url: z.string().url(),
  long_url: z.string().url()
})

export type ShortenResponse = z.infer<typeof shortenResponseSchema>

function normalizeUrlInput(value: string): string {
  const trimmedValue = value.trim()
  if (!trimmedValue) {
    return trimmedValue
  }

  const hasScheme = /^[a-zA-Z][a-zA-Z\d+.-]*:\/\//.test(trimmedValue)
  if (hasScheme) {
    return trimmedValue
  }

  return `https://${trimmedValue}`
}

export async function createShortUrl(longUrl: string): Promise<ShortenResponse> {
  const payload = shortenRequestSchema.parse({ url: normalizeUrlInput(longUrl) })

  const response = await fetch(`${API_BASE_URL}/shorten`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || "Failed to shorten URL")
  }

  const json = await response.json()
  return shortenResponseSchema.parse(json)
}
