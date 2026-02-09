import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/Card"
import { Label } from "@/components/ui/Label"
import { Textarea } from "@/components/ui/Textarea"
import { Progress } from "@/components/ui/Progress"
import { api } from "@/lib/api"
import type { BlueprintSession, BlueprintQuestion } from "@/types"
import { Loader2, ArrowRight, CheckCircle } from "lucide-react"

export function BlueprintBuilder() {
  const [topic, setTopic] = useState("")
  const [session, setSession] = useState<BlueprintSession | null>(null)
  const [currentAnswer, setCurrentAnswer] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const startSession = async () => {
    if (!topic.trim()) return
    setIsLoading(true)
    setError(null)
    try {
      const response = await api.startBlueprint(topic)
      setSession(response.data)
    } catch (err: any) {
      setError(err.response?.data?.message || "Failed to start blueprint session")
    } finally {
      setIsLoading(false)
    }
  }

  const submitAnswer = async () => {
    if (!session || !currentAnswer.trim()) return
    setIsLoading(true)
    setError(null)
    try {
      const response = await api.answerBlueprint(session.id, currentAnswer)
      setSession(response.data)
      setCurrentAnswer("")
    } catch (err: any) {
      setError(err.response?.data?.message || "Failed to submit answer")
    } finally {
      setIsLoading(false)
    }
  }

  // Show completion screen
  if (session?.isComplete) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-6 w-6 text-green-500" />
            Blueprint Complete
          </CardTitle>
          <CardDescription>
            Your governance blueprint has been generated successfully
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">
            Based on your responses, we&apos;ve created a comprehensive governance blueprint for: <strong>{topic}</strong>
          </p>
        </CardContent>
        <CardFooter className="flex gap-2">
          <Button onClick={() => navigate("/blueprints")}>
            View Blueprint
          </Button>
          <Button variant="outline" onClick={() => navigate("/")}>
            Back to Home
          </Button>
        </CardFooter>
      </Card>
    )
  }

  // Show topic input to start
  if (!session) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Blueprint Builder</CardTitle>
          <CardDescription>
            Answer a series of questions to generate a custom governance blueprint for your organization
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <div className="rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
              {error}
            </div>
          )}
          <div className="space-y-2">
            <Label htmlFor="topic">What topic would you like to create a blueprint for?</Label>
            <Input
              id="topic"
              placeholder="e.g., AI Ethics Policy, Data Retention Guidelines, Model Governance..."
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />
          </div>
        </CardContent>
        <CardFooter>
          <Button 
            onClick={startSession} 
            disabled={isLoading || !topic.trim()}
            className="w-full"
          >
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Start Building
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </CardFooter>
      </Card>
    )
  }

  // Show question form
  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Blueprint Interview</CardTitle>
          <span className="text-sm text-muted-foreground">
            {Math.round(session.progress * 100)}% Complete
          </span>
        </div>
        <Progress value={session.progress * 100} className="mt-2" />
        <CardDescription className="mt-2">
          Topic: {session.topic}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <div className="rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
            {error}
          </div>
        )}
        {session.currentQuestion && (
          <div className="space-y-4">
            <div className="rounded-lg bg-muted p-4">
              <p className="font-medium">{session.currentQuestion.question}</p>
              {session.currentQuestion.context && (
                <p className="mt-2 text-sm text-muted-foreground">
                  {session.currentQuestion.context}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="answer">Your Answer</Label>
              {session.currentQuestion.type === "text" ? (
                <Textarea
                  id="answer"
                  placeholder="Type your answer here..."
                  value={currentAnswer}
                  onChange={(e) => setCurrentAnswer(e.target.value)}
                  rows={4}
                />
              ) : session.currentQuestion.type === "choice" ? (
                <div className="space-y-2">
                  {session.currentQuestion.options?.map((option) => (
                    <Button
                      key={option}
                      variant={currentAnswer === option ? "default" : "outline"}
                      className="w-full justify-start"
                      onClick={() => setCurrentAnswer(option)}
                    >
                      {option}
                    </Button>
                  ))}
                </div>
              ) : null}
            </div>
          </div>
        )}
      </CardContent>
      <CardFooter>
        <Button
          onClick={submitAnswer}
          disabled={isLoading || !currentAnswer.trim()}
          className="w-full"
        >
          {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Continue
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </CardFooter>
    </Card>
  )
}