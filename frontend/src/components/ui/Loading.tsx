import * as React from "react"
import { cn } from "@/lib/utils"

const Loading = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { size?: 'sm' | 'md' | 'lg' }
>(({ className, size = 'md', ...props }, ref) => {
  const sizeClasses = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-2',
    lg: 'h-12 w-12 border-3',
  }

  return (
    <div
      ref={ref}
      className={cn("flex items-center justify-center", className)}
      {...props}
    >
      <div
        className={cn(
          "animate-spin rounded-full border-solid border-current border-t-transparent",
          sizeClasses[size],
          "text-primary"
        )}
      />
    </div>
  )
})
Loading.displayName = "Loading"

const LoadingPage = () => (
  <div className="flex h-screen w-full items-center justify-center">
    <Loading size="lg" />
  </div>
)

const LoadingOverlay = ({ message }: { message?: string }) => (
  <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-background/80 backdrop-blur-sm">
    <Loading size="lg" />
    {message && (
      <p className="mt-4 text-sm text-muted-foreground">{message}</p>
    )}
  </div>
)

export { Loading, LoadingPage, LoadingOverlay }