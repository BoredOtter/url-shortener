import { afterEach, describe, expect, it, vi } from "vitest"

import { createShortUrl } from "./api"

afterEach(() => {
  vi.restoreAllMocks()
})

describe("createShortUrl", () => {
  it("normalizes urls without a scheme before sending", async () => {
    const fetchSpy = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(
        new Response(
          JSON.stringify({
            short_url: "https://short.local/api/abc123",
            long_url: "https://example.com/path"
          }),
          { status: 200 }
        )
      )

    const result = await createShortUrl("example.com/path")

    expect(result).toEqual({
      short_url: "https://short.local/api/abc123",
      long_url: "https://example.com/path"
    })

    expect(fetchSpy).toHaveBeenCalledWith(
      expect.stringMatching(/\/api\/shorten$/),
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: "https://example.com/path" })
      })
    )
  })

  it("throws backend message when request fails", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("Service unavailable", { status: 503 }))

    await expect(createShortUrl("https://example.com")).rejects.toThrow("Service unavailable")
  })

  it("rejects empty urls", async () => {
    await expect(createShortUrl("   ")).rejects.toThrow()
  })
})
