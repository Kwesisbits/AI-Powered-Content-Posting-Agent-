import LoginForm from '@/components/auth/login-form'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { SystemStatus } from '@/components/system-status'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="mb-8 md:mb-12">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
                🤖 AI Content Agent System
              </h1>
              <p className="text-gray-600 mt-2">
                AI-powered content creation with human-in-the-loop approvals
              </p>
            </div>
            <SystemStatus />
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Login */}
          <div className="lg:col-span-2">
            <Card className="border-2 border-primary/10 shadow-lg">
              <CardHeader>
                <CardTitle className="text-2xl">Welcome Back</CardTitle>
                <CardDescription>
                  Sign in with your demo credentials to access the AI Content Agent
                </CardDescription>
              </CardHeader>
              <CardContent>
                <LoginForm />
                
                {/* Demo Credentials */}
                <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <h3 className="font-semibold text-blue-900 mb-2">Demo Credentials</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div className="bg-white p-3 rounded border">
                      <div className="font-medium text-gray-900">Admin</div>
                      <div className="text-sm text-gray-600">admin@demo.com</div>
                      <div className="text-sm text-gray-600">demo123</div>
                      <div className="text-xs text-blue-600 mt-1">Full system access</div>
                    </div>
                    <div className="bg-white p-3 rounded border">
                      <div className="font-medium text-gray-900">Reviewer</div>
                      <div className="text-sm text-gray-600">reviewer@demo.com</div>
                      <div className="text-sm text-gray-600">demo123</div>
                      <div className="text-xs text-blue-600 mt-1">Approve/reject content</div>
                    </div>
                    <div className="bg-white p-3 rounded border">
                      <div className="font-medium text-gray-900">Client</div>
                      <div className="text-sm text-gray-600">client@demo.com</div>
                      <div className="text-sm text-gray-600">demo123</div>
                      <div className="text-xs text-blue-600 mt-1">Create & submit content</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Features */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span className="text-blue-600">🚀</span> Key Features
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <span className="text-green-600">🤖</span>
                  </div>
                  <div>
                    <h4 className="font-medium">AI Content Generation</h4>
                    <p className="text-sm text-gray-600">Local LLM with Gemma 7B</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <span className="text-blue-600">👁️</span>
                  </div>
                  <div>
                    <h4 className="font-medium">Human-in-the-Loop</h4>
                    <p className="text-sm text-gray-600">Strict approval workflow</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-red-100 rounded-lg">
                    <span className="text-red-600">⚠️</span>
                  </div>
                  <div>
                    <h4 className="font-medium">Emergency Controls</h4>
                    <p className="text-sm text-gray-600">Pause, Manual, Crisis modes</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <span className="text-purple-600">📊</span>
                  </div>
                  <div>
                    <h4 className="font-medium">Platform Analytics</h4>
                    <p className="text-sm text-gray-600">Mock posting & metrics</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span className="text-purple-600">⚡</span> Quick Demo
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ol className="space-y-3 text-sm">
                  <li className="flex items-start gap-2">
                    <span className="bg-primary text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">1</span>
                    <span>Login as <strong>client@demo.com</strong></span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="bg-primary text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">2</span>
                    <span>Upload media & generate content</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="bg-primary text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">3</span>
                    <span>Submit for approval</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="bg-primary text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">4</span>
                    <span>Login as <strong>reviewer@demo.com</strong></span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="bg-primary text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">5</span>
                    <span>Approve/reject content</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="bg-primary text-white rounded-full w-5 h-5 flex items-center justify-center text-xs">6</span>
                    <span>Test emergency controls as admin</span>
                  </li>
                </ol>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-12 pt-8 border-t text-center text-gray-500 text-sm">
          <p>Built for the Native AI Engineer role at 40 Analytics</p>
          <p className="mt-1">Backend: FastAPI + Ollama (Gemma 7B) | Frontend: Next.js 14</p>
        </footer>
      </div>
    </div>
  )
}
