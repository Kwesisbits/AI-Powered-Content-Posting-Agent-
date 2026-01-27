'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/components/providers/auth-provider'
import { api } from '@/lib/api'
import toast from 'react-hot-toast'
import { 
  AlertTriangle, 
  PauseCircle, 
  PlayCircle, 
  Shield, 
  AlertCircle,
  Settings,
  Zap
} from 'lucide-react'

export default function ControlPage() {
  const { user } = useAuth()
  const [isLoading, setIsLoading] = useState<string | null>(null)

  const handleControlAction = async (action: string, notes?: string) => {
    if (!user || user.role !== 'admin') {
      toast.error('Only administrators can use system controls')
      return
    }

    setIsLoading(action)
    try {
      const response = await api.post('/control/pause', {
        action,
        notes,
      })
      
      toast.success(`System ${action.replace('_', ' ')} executed successfully`)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to execute control action')
    } finally {
      setIsLoading(null)
    }
  }

  const handleEmergencyPause = () => {
    if (confirm(' EMERGENCY PAUSE\n\nThis will immediately halt all automation. Are you sure?')) {
      handleControlAction('pause', 'Emergency pause initiated')
    }
  }

  const handleCrisisMode = () => {
    if (confirm(' CRISIS MODE ACTIVATION\n\nThis will:\n1. Halt all automation\n2. Cancel scheduled posts\n3. Notify all admins\n4. Require manual reset\n\nAre you sure?')) {
      handleControlAction('set_crisis', 'Crisis mode activated')
    }
  }

  if (!user || user.role !== 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">Access Denied</h2>
          <p className="text-gray-600">Only administrators can access system controls.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-red-50 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Shield className="h-8 w-8 text-red-600" />
            System Control Panel
          </h1>
          <p className="text-gray-600 mt-2">
            Emergency controls and system management. Use with caution.
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Emergency Controls */}
          <div className="lg:col-span-2 space-y-6">
            {/* Emergency Controls */}
            <Card className="border-2 border-red-200 emergency-mode">
              <CardHeader className="bg-red-50">
                <CardTitle className="flex items-center gap-2 text-red-700">
                  <AlertTriangle className="h-5 w-5" />
                  Emergency Controls
                </CardTitle>
                <CardDescription className="text-red-600">
                  Immediate system-wide actions
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <h3 className="font-semibold text-red-800 mb-2">Instant Pause</h3>
                    <p className="text-sm text-red-600 mb-3">
                      Immediately halts all automated actions. Queued posts remain in queue.
                    </p>
                    <Button
                      variant="emergency"
                      className="w-full"
                      onClick={handleEmergencyPause}
                      disabled={isLoading !== null}
                    >
                      <PauseCircle className="mr-2 h-4 w-4" />
                      {isLoading === 'pause' ? 'Pausing...' : 'INSTANT PAUSE'}
                    </Button>
                  </div>

                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <h3 className="font-semibold text-red-800 mb-2">Crisis Mode</h3>
                    <p className="text-sm text-red-600 mb-3">
                      Emergency shutdown. Cancels all scheduled posts and requires manual reset.
                    </p>
                    <Button
                      variant="emergency"
                      className="w-full"
                      onClick={handleCrisisMode}
                      disabled={isLoading !== null}
                    >
                      <AlertCircle className="mr-2 h-4 w-4" />
                      {isLoading === 'set_crisis' ? 'Activating...' : 'ACTIVATE CRISIS MODE'}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* System Modes */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  System Modes
                </CardTitle>
                <CardDescription>
                  Configure automation levels
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 border rounded-lg">
                    <h3 className="font-semibold mb-2">Normal Mode</h3>
                    <p className="text-sm text-gray-600 mb-3">
                      Full automation enabled with approval workflow
                    </p>
                    <Button
                      variant="default"
                      className="w-full"
                      onClick={() => handleControlAction('set_normal')}
                      disabled={isLoading !== null}
                    >
                      <Zap className="mr-2 h-4 w-4" />
                      Set Normal
                    </Button>
                  </div>

                  <div className="p-4 border rounded-lg">
                    <h3 className="font-semibold mb-2">Manual Mode</h3>
                    <p className="text-sm text-gray-600 mb-3">
                      AI generates content but all actions require manual approval
                    </p>
                    <Button
                      variant="warning"
                      className="w-full"
                      onClick={() => handleControlAction('set_manual')}
                      disabled={isLoading !== null}
                    >
                      <PauseCircle className="mr-2 h-4 w-4" />
                      Set Manual
                    </Button>
                  </div>

                  <div className="p-4 border rounded-lg">
                    <h3 className="font-semibold mb-2">Resume Automation</h3>
                    <p className="text-sm text-gray-600 mb-3">
                      Resume normal operations after pause
                    </p>
                    <Button
                      variant="success"
                      className="w-full"
                      onClick={() => handleControlAction('resume')}
                      disabled={isLoading !== null}
                    >
                      <PlayCircle className="mr-2 h-4 w-4" />
                      Resume
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Status & Logs */}
          <div className="space-y-6">
            {/* System Status */}
            <Card>
              <CardHeader>
                <CardTitle>System Status</CardTitle>
                <CardDescription>Current system state</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span className="font-medium">Automation Status</span>
                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                      Active
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span className="font-medium">Approval Workflow</span>
                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                      Enabled
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span className="font-medium">AI Generation</span>
                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                      Online
                    </span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                    <span className="font-medium">Scheduled Posts</span>
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                      3 Pending
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recent Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Control Actions</CardTitle>
                <CardDescription>Last 5 system changes</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    { action: 'System started', time: '2 hours ago', user: 'system' },
                    { action: 'Content generated', time: '1 hour ago', user: 'client@demo.com' },
                    { action: 'Approval requested', time: '45 minutes ago', user: 'client@demo.com' },
                    { action: 'Post scheduled', time: '30 minutes ago', user: 'reviewer@demo.com' },
                    { action: 'Login', time: '15 minutes ago', user: 'admin@demo.com' },
                  ].map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-2 border-b last:border-0">
                      <div>
                        <p className="text-sm font-medium">{item.action}</p>
                        <p className="text-xs text-gray-500">by {item.user}</p>
                      </div>
                      <span className="text-xs text-gray-500">{item.time}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Instructions */}
            <Card>
              <CardHeader>
                <CardTitle>Instructions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-start gap-2">
                  <div className="h-2 w-2 bg-red-500 rounded-full mt-2"></div>
                  <p className="text-sm">Emergency controls require confirmation</p>
                </div>
                <div className="flex items-start gap-2">
                  <div className="h-2 w-2 bg-yellow-500 rounded-full mt-2"></div>
                  <p className="text-sm">All actions are logged in audit trail</p>
                </div>
                <div className="flex items-start gap-2">
                  <div className="h-2 w-2 bg-blue-500 rounded-full mt-2"></div>
                  <p className="text-sm">Crisis mode requires manual reset</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
