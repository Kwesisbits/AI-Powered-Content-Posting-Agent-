'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@/components/providers/auth-provider'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  Clock, 
  BarChart3,
  AlertTriangle,
  Zap,
  Users
} from 'lucide-react'
import { api } from '@/lib/api'
import { formatDate, truncateText } from '@/lib/utils'
import Link from 'next/link'

interface DashboardStats {
  total_drafts: number
  pending_approvals: number
  scheduled_posts: number
  published_posts: number
}

interface RecentActivity {
  id: number
  action: string
  timestamp: string
  details: any
}

export default function DashboardPage() {
  const { user } = useAuth()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (user) {
      fetchDashboardData()
    }
  }, [user])

  const fetchDashboardData = async () => {
    try {
      // Fetch stats
      const draftsRes = await api.get('/content/drafts')
      const approvalsRes = await api.get('/approval/pending')
      const scheduledRes = await api.get('/posts/scheduled?status=pending')
      const publishedRes = await api.get('/posts/scheduled?status=posted')

      setStats({
        total_drafts: draftsRes.data.length,
        pending_approvals: approvalsRes.data.length,
        scheduled_posts: scheduledRes.data.length,
        published_posts: publishedRes.data.length,
      })

      // Mock recent activity
      setRecentActivity([
        { id: 1, action: 'content_generated', timestamp: new Date().toISOString(), details: { platform: 'LinkedIn' } },
        { id: 2, action: 'approval_requested', timestamp: new Date(Date.now() - 3600000).toISOString(), details: { draft_id: 1 } },
        { id: 3, action: 'post_scheduled', timestamp: new Date(Date.now() - 7200000).toISOString(), details: { platform: 'Twitter' } },
      ])
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Please sign in</h2>
          <p>You need to be logged in to access the dashboard.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-gray-600 mt-1">
                Welcome back, {user.full_name || user.email} • {user.role.charAt(0).toUpperCase() + user.role.slice(1)} Access
              </p>
            </div>
            
            <div className="flex gap-3">
              {user.role === 'client' && (
                <Link href="/content/new">
                  <Button className="gap-2">
                    <Upload className="h-4 w-4" />
                    Create Content
                  </Button>
                </Link>
              )}
              
              {user.role === 'reviewer' && (
                <Link href="/approvals">
                  <Button className="gap-2" variant="secondary">
                    <CheckCircle className="h-4 w-4" />
                    Review Approvals
                  </Button>
                </Link>
              )}
              
              {user.role === 'admin' && (
                <Link href="/control">
                  <Button className="gap-2" variant="destructive">
                    <AlertTriangle className="h-4 w-4" />
                    System Controls
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Total Drafts</p>
                  <p className="text-2xl font-bold mt-2">
                    {loading ? '...' : stats?.total_drafts || 0}
                  </p>
                </div>
                <div className="p-3 bg-blue-100 rounded-lg">
                  <FileText className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Pending Approvals</p>
                  <p className="text-2xl font-bold mt-2">
                    {loading ? '...' : stats?.pending_approvals || 0}
                  </p>
                </div>
                <div className="p-3 bg-yellow-100 rounded-lg">
                  <Clock className="h-6 w-6 text-yellow-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Scheduled Posts</p>
                  <p className="text-2xl font-bold mt-2">
                    {loading ? '...' : stats?.scheduled_posts || 0}
                  </p>
                </div>
                <div className="p-3 bg-green-100 rounded-lg">
                  <Zap className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Published Posts</p>
                  <p className="text-2xl font-bold mt-2">
                    {loading ? '...' : stats?.published_posts || 0}
                  </p>
                </div>
                <div className="p-3 bg-purple-100 rounded-lg">
                  <BarChart3 className="h-6 w-6 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="activity" className="space-y-6">
          <TabsList>
            <TabsTrigger value="activity">Recent Activity</TabsTrigger>
            <TabsTrigger value="quick-actions">Quick Actions</TabsTrigger>
            <TabsTrigger value="system">System Info</TabsTrigger>
          </TabsList>

          <TabsContent value="activity">
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>Latest actions in the system</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentActivity.map((activity) => (
                    <div key={activity.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-gray-100 rounded">
                          <Users className="h-4 w-4" />
                        </div>
                        <div>
                          <p className="font-medium">
                            {activity.action.replace('_', ' ').charAt(0).toUpperCase() + 
                             activity.action.replace('_', ' ').slice(1)}
                          </p>
                          <p className="text-sm text-gray-500">
                            {formatDate(activity.timestamp)}
                          </p>
                        </div>
                      </div>
                      <Button variant="ghost" size="sm">
                        View
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="quick-actions">
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>Based on your role</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {user.role === 'client' && (
                    <>
                      <Link href="/content/new">
                        <Card className="cursor-pointer hover:border-primary transition-colors">
                          <CardContent className="p-6">
                            <div className="flex items-center gap-3">
                              <Upload className="h-5 w-5 text-primary" />
                              <div>
                                <h3 className="font-semibold">Generate Content</h3>
                                <p className="text-sm text-gray-500">Create new AI content</p>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </Link>
                      <Link href="/content">
                        <Card className="cursor-pointer hover:border-primary transition-colors">
                          <CardContent className="p-6">
                            <div className="flex items-center gap-3">
                              <FileText className="h-5 w-5 text-primary" />
                              <div>
                                <h3 className="font-semibold">My Drafts</h3>
                                <p className="text-sm text-gray-500">View all your content drafts</p>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </Link>
                    </>
                  )}

                  {user.role === 'reviewer' && (
                    <>
                      <Link href="/approvals">
                        <Card className="cursor-pointer hover:border-primary transition-colors">
                          <CardContent className="p-6">
                            <div className="flex items-center gap-3">
                              <CheckCircle className="h-5 w-5 text-primary" />
                              <div>
                                <h3 className="font-semibold">Review Approvals</h3>
                                <p className="text-sm text-gray-500">Approve or reject content</p>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </Link>
                    </>
                  )}

                  {user.role === 'admin' && (
                    <>
                      <Link href="/control">
                        <Card className="cursor-pointer hover:border-destructive transition-colors">
                          <CardContent className="p-6">
                            <div className="flex items-center gap-3">
                              <AlertTriangle className="h-5 w-5 text-destructive" />
                              <div>
                                <h3 className="font-semibold">System Controls</h3>
                                <p className="text-sm text-gray-500">Emergency controls & settings</p>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </Link>
                      <Link href="/analytics">
                        <Card className="cursor-pointer hover:border-primary transition-colors">
                          <CardContent className="p-6">
                            <div className="flex items-center gap-3">
                              <BarChart3 className="h-5 w-5 text-primary" />
                              <div>
                                <h3 className="font-semibold">Analytics</h3>
                                <p className="text-sm text-gray-500">View system performance</p>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </Link>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="system">
            <Card>
              <CardHeader>
                <CardTitle>System Information</CardTitle>
                <CardDescription>Platform status and configuration</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 border rounded-lg">
                      <h3 className="font-semibold mb-2">AI Model</h3>
                      <p className="text-gray-600">Gemma 7B (via Ollama)</p>
                    </div>
                    <div className="p-4 border rounded-lg">
                      <h3 className="font-semibold mb-2">API Status</h3>
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-2 rounded-full bg-green-500"></div>
                        <span className="text-green-600">Operational</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
