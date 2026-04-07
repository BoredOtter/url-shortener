import { useState } from "react"
import { createShortUrl } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

function App() {
  const [url, setUrl] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [shortUrl, setShortUrl] = useState<string | null>(null)
  const [longUrl, setLongUrl] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setLoading(true)
    setError(null)
    setCopied(false)

    try {
      const data = await createShortUrl(url)
      setShortUrl(data.short_url)
      setLongUrl(data.long_url)
    } catch (submitError) {
      setShortUrl(null)
      setLongUrl(null)
      setError(submitError instanceof Error ? submitError.message : "Failed to shorten URL")
    } finally {
      setLoading(false)
    }
  }

  async function onCopy() {
    if (!shortUrl) {
      return
    }

    await navigator.clipboard.writeText(shortUrl)
    setCopied(true)
    setTimeout(() => setCopied(false), 1200)
  }

  return (
    <main className="mx-auto flex min-h-svh w-full max-w-3xl flex-col justify-center gap-6 px-4 py-10">
      <header className="space-y-2">
        <p className="text-sm text-muted-foreground">Simple URL shortener</p>
        <p className="text-muted-foreground">Paste a long URL and get a short, shareable link.</p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>Create short URL</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="url-input">Long URL</Label>
              <Input
                id="url-input"
                type="text"
                inputMode="url"
                value={url}
                onChange={(event) => setUrl(event.target.value)}
                placeholder="example.com/very/long/link"
                required
              />
            </div>

            <Button type="submit" disabled={loading}>
              {loading ? "Shortening..." : "Shorten"}
            </Button>
          </form>
        </CardContent>
      </Card>

      {(shortUrl || error) && (
        <Card>
          <CardHeader>
            <CardTitle>{error ? "Request failed" : "Your short URL"}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {error ? (
              <p className="text-sm text-destructive">{error}</p>
            ) : (
              <>
                <a className="text-sm font-medium text-primary underline underline-offset-4" href={shortUrl ?? "#"} target="_blank" rel="noreferrer">
                  {shortUrl}
                </a>
                <p className="text-sm text-muted-foreground break-all">Original: {longUrl}</p>
                <Button variant="secondary" onClick={onCopy}>
                  {copied ? "Copied" : "Copy link"}
                </Button>
              </>
            )}
          </CardContent>
        </Card>
      )}
    </main>
  )
}


export default App
