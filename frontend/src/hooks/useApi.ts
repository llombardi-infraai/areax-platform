import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'

// Generic hook for API queries
export function useApiQuery<T>(
  key: string[],
  fetchFn: () => Promise<T>,
  options?: { enabled?: boolean }
) {
  return useQuery({
    queryKey: key,
    queryFn: fetchFn,
    enabled: options?.enabled ?? true,
  })
}

// Generic hook for API mutations
export function useApiMutation<T, D = unknown>(
  mutationFn: (data: D) => Promise<T>,
  invalidateKeys?: string[][]
) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn,
    onSuccess: () => {
      invalidateKeys?.forEach((key) => {
        queryClient.invalidateQueries({ queryKey: key })
      })
    },
  })
}