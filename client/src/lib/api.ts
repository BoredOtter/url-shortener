import { z } from "zod"

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "")

const shortenRequestSchema = z.object({
  url: z.string().url("Enter a valid URL")
})

const shortenResponseSchema = z.object({
  short_url: z.string().url(),
  long_url: z.string().url()
})

export type ShortenResponse = z.infer<typeof shortenResponseSchema>

export async function createShortUrl(longUrl: string): Promise<ShortenResponse> {
  const payload = shortenRequestSchema.parse({ url: longUrl })

  const response = await fetch(`${API_BASE_URL}/api/shorten`, {
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
