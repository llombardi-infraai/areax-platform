import { useState, useEffect } from "react"
import { QRCodeSVG } from "qrcode.react"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"
import { Label } from "@/components/ui/Label"
import { Alert, AlertDescription } from "@/components/ui/Alert"
import { api } from "@/lib/api"
import { useNavigate } from "react-router-dom"
import { Copy, Loader2, CheckCircle } from "lucide-react"

export function MFASetup() {
  const [secret, setSecret] = useState("")
  const [qrCode, setQrCode] = useState("")
  const [backupCodes, setBackupCodes] = useState<string[]>([])
  const [code, setCode] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isComplete, setIsComplete] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    const setupMFA = async () => {
      try {
        const response = await api.setupMFA()
        const data = response.data
        setSecret(data.secret)
        setQrCode(data.qrCode)
        setBackupCodes(data.backupCodes)
      } catch (err: any) {
        setError(err.response?.data?.message || "Failed to setup MFA")
      }
    }
    setupMFA()
  }, [])

  const handleCopySecret = () => {
    navigator.clipboard.writeText(secret)
  }

  const handleCopyBackupCodes = () => {
    navigator.clipboard.writeText(backupCodes.join("\n"))
  }

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      await api.confirmMFA(code, secret)
      setIsComplete(true)
    } catch (err: any) {
      setError(err.response?.data?.message || "Verification failed")
    } finally {
      setIsLoading(false)
    }
  }

  if (isComplete) {
    return (
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-6 w-6 text-green-500" />
            MFA Enabled
          </CardTitle>
          <CardDescription>
            Two-factor authentication has been successfully set up for your account.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            Make sure to save your backup codes in a secure location. You will need them if you lose access to your authenticator app.
          </p>
          <Button onClick={() => navigate("/")} className="w-full">
            Continue to Dashboard
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Set Up Two-Factor Authentication</CardTitle>
        <CardDescription>
          Scan the QR code with your authenticator app to enable 2FA
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* QR Code */}
        {qrCode && (
          <div className="flex flex-col items-center space-y-4">
            <div className="rounded-lg border p-4 bg-white">
              <QRCodeSVG value={qrCode} size={200} />
            </div>
            <div className="flex items-center gap-2 text-sm">
              <code className="rounded bg-muted px-2 py-1">{secret}</code>
              <Button variant="ghost" size="sm" onClick={handleCopySecret}>
                <Copy className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground text-center">
              Can&apos;t scan? Enter the code above manually into your authenticator app
            </p>
          </div>
        )}

        {/* Verification Code */}
        <form onSubmit={handleVerify} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="verify-code">Verification Code</Label>
            <Input
              id="verify-code"
              type="text"
              inputMode="numeric"
              pattern="[0-9]*"
              maxLength={6}
              placeholder="Enter 6-digit code"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              required
            />
          </div>
          <Button
            type="submit"
            className="w-full"
            disabled={isLoading || code.length !== 6}
          >
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Verify and Enable
          </Button>
        </form>

        {/* Backup Codes */}
        {backupCodes.length > 0 && (
          <div className="rounded-lg border p-4 space-y-2">
            <div className="flex items-center justify-between">
              <Label>Backup Codes</Label>
              <Button variant="ghost" size="sm" onClick={handleCopyBackupCodes}>
                <Copy className="h-4 w-4 mr-1" />
                Copy all
              </Button>
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              {backupCodes.map((code, i) => (
                <code key={i} className="rounded bg-muted px-2 py-1 text-center font-mono">
                  {code}
                </code>
              ))}
            </div>
            <p className="text-xs text-muted-foreground">
              Save these codes securely. Each can be used once if you lose access to your authenticator.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}