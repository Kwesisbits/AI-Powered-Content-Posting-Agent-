'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { api } from '@/lib/api'
import { Activity, AlertCircle, CheckCircle, PauseCircle, Shield } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SystemStatusData {
  mode: 'normal' | 'manual' | 'crisis'
  is_paused: boolean
  last_updated_at: string
  can_auto_approve: boolean
  can_auto_post: boolean
}

export function SystemStatus() {
  const [status, setStatus] = useState<SystemStatusData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchStatus = async () => {
    try {
      const response = await api.get('/control/status')
      setStatus(response.data)
    } catch (error) {
      console.error('Failed to fetch system status:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Card className="w-full max-w-md">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="animate-pulse h-4 bg-gray-200 rounded w-24"></div>
            <div className="animate-pulse h-4 bg-gray-200 rounded w-16"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const getModeIcon = () => {
    if (!status) return <Activity className="h-4 w-4" />
    if (status.mode === 'crisis') return <AlertCircle className="h-4 w-4" />
    if (status.mode === 'manual') return <PauseCircle className="h-4 w-4" />
    return <CheckCircle className="h-4 w-4" />
  }

  const getModeColor = () => {
    if (!status) return 'bg-gray-100 text-gray-800'
    if (status.mode === 'crisis') return 'bg-red-100 text-red-800'
    if (status.mode === 'manual') return 'bg-yellow-100 text-yellow-800'
    return 'bg-green-100 text-green-800'
  }

  return (
    <Card className="w-full max-w-md">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-gray-500" />
            <span className="font-medium">System Status</span>
          </div>
          <div className="flex items-center gap-2">
            {status?.is_paused && (
              <Badge variant="destructive" className="animate-pulse">
                PAUSED
              </Badge>
            )}
            <Badge className={cn(getModeColor(), 'capitalize')}>
              {getModeIcon()}
              <span className="ml-1">{status?.mode || 'unknown'}</span>
            </Badge>
          </div>
        </div>
        
        {status && (
          <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
            <div className="flex items-center gap-2">
              <div className={cn(
                'h-2 w-2 rounded-full',
                status.can_auto_approve ? 'bg-green-500' : 'bg-gray-300'
              )} />
              <span className="text-gray-600">Auto-approve</span>
            </div>
            <div className="flex items-center gap-2">
              <div className={cn(
                'h-2 w-2 rounded-full',
                status.can_auto_post ? 'bg-green-500' : 'bg-gray-300'
              )} />
              <span className="text-gray-600">Auto-post</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
