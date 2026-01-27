'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useAuth } from '@/components/providers/auth-provider'
import { api } from '@/lib/api'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'
import { Loader2, Upload, Sparkles } from 'lucide-react'

const contentSchema = z.object({
  platform: z.enum(['linkedin', 'instagram', 'twitter']),
  context: z.string().optional(),
  prompt_override: z.string().optional(),
})

type ContentFormData = z.infer<typeof contentSchema>

export default function NewContentPage() {
  const { user } = useAuth()
  const router = useRouter()
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedContent, setGeneratedContent] = useState<string | null>(null)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<ContentFormData>({
    resolver: zodResolver(contentSchema),
    defaultValues: {
      platform: 'linkedin',
    },
  })

  const platform = watch('platform')

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files))
    }
  }

  const onSubmit = async (data: ContentFormData) => {
    if (!user) return

    setIsGenerating(true)
    try {
      // Upload files if any
      const mediaAssetIds: number[] = []
      if (selectedFiles.length > 0) {
        for (const file of selectedFiles) {
          const formData = new FormData()
          formData.append('file', file)
          const uploadRes = await api.post('/media/upload', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          })
          mediaAssetIds.push(uploadRes.data.id)
        }
      }

      // Generate content
      const response = await api.post('/content/generate', {
        ...data,
        media_asset_ids: mediaAssetIds.length > 0 ? mediaAssetIds : undefined,
      })

      setGeneratedContent(response.data.content_text)
      toast.success('Content generated successfully!')
      
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to generate content')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleSaveDraft = async () => {
    if (!generatedContent || !user) return

    try {
      await api.post('/content/drafts', {
        platform,
        content_text: generatedContent,
        status: 'draft',
      })
      
      toast.success('Draft saved successfully!')
      router.push('/content')
    } catch (error) {
      toast.error('Failed to save draft')
    }
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Please sign in</h2>
          <p>You need to be logged in to create content.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Create AI Content</h1>
          <p className="text-gray-600 mt-2">
            Generate platform-specific content using AI
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Form */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary" />
                  Content Generation
                </CardTitle>
                <CardDescription>
                  Configure your content preferences and let AI do the writing
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                  {/* Platform Selection */}
                  <div className="space-y-2">
                    <Label htmlFor="platform">Platform</Label>
                    <Select {...register('platform')}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select platform" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="linkedin">LinkedIn</SelectItem>
                        <SelectItem value="instagram">Instagram</SelectItem>
                        <SelectItem value="twitter">Twitter/X</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-sm text-gray-500">
                      {platform === 'linkedin' && 'Professional tone, business focus'}
                      {platform === 'instagram' && 'Visual, engaging, emoji-friendly'}
                      {platform === 'twitter' && 'Concise, trending topics, hashtags'}
                    </p>
                  </div>

                  {/* Media Upload */}
                  <div className="space-y-2">
                    <Label>Media Upload (Optional)</Label>
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                      <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600 mb-2">
                        Drag & drop images or videos, or click to browse
                      </p>
                      <Input
                        type="file"
                        multiple
                        accept="image/*,video/*"
                        onChange={handleFileSelect}
                        className="hidden"
                        id="file-upload"
                      />
                      <Label
                        htmlFor="file-upload"
                        className="cursor-pointer inline-block px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90"
                      >
                        Browse Files
                      </Label>
                      {selectedFiles.length > 0 && (
                        <div className="mt-4">
                          <p className="text-sm font-medium">Selected files:</p>
                          <ul className="text-sm text-gray-600 mt-1">
                            {selectedFiles.map((file, index) => (
                              <li key={index}>• {file.name}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Context Input */}
                  <div className="space-y-2">
                    <Label htmlFor="context">Context / Topic</Label>
                    <Textarea
                      id="context"
                      placeholder="What should this content be about? (e.g., AI automation, team updates, product launch)"
                      rows={3}
                      {...register('context')}
                    />
                    <p className="text-sm text-gray-500">
                      Provide context to help AI generate more relevant content
                    </p>
                  </div>

                  {/* Custom Prompt */}
                  <div className="space-y-2">
                    <Label htmlFor="prompt_override">Custom Prompt (Optional)</Label>
                    <Textarea
                      id="prompt_override"
                      placeholder="Override the default AI prompt (advanced)"
                      rows={2}
                      {...register('prompt_override')}
                    />
                    <p className="text-sm text-gray-500">
                      Leave empty for AI to use platform-specific templates
                    </p>
                  </div>

                  {/* Generate Button */}
                  <Button type="submit" className="w-full" disabled={isGenerating}>
                    {isGenerating ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Generating Content...
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Generate AI Content
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Preview */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Generated Content</CardTitle>
                <CardDescription>
                  {generatedContent ? 'AI-generated content preview' : 'Content will appear here'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {generatedContent ? (
                  <div className="space-y-4">
                    <div className="p-4 bg-gray-50 rounded-lg border">
                      <div className="flex items-center gap-2 mb-2">
                        <div className={`h-3 w-3 rounded-full ${
                          platform === 'linkedin' ? 'bg-blue-500' :
                          platform === 'instagram' ? 'bg-gradient-to-r from-purple-500 to-pink-500' :
                          'bg-sky-500'
                        }`} />
                        <span className="font-medium capitalize">{platform}</span>
                      </div>
                      <p className="whitespace-pre-wrap">{generatedContent}</p>
                    </div>
                    
                    <div className="flex gap-2">
                      <Button onClick={handleSaveDraft} className="flex-1">
                        Save as Draft
                      </Button>
                      <Button 
                        variant="secondary" 
                        onClick={() => setGeneratedContent(null)}
                        className="flex-1"
                      >
                        Regenerate
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="text-center p-8 border-2 border-dashed border-gray-300 rounded-lg">
                    <Sparkles className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">
                      Generate content to see the AI's creation here
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Platform Tips */}
            <Card>
              <CardHeader>
                <CardTitle>Platform Tips</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {platform === 'linkedin' && (
                  <>
                    <div className="flex items-start gap-2">
                      <div className="h-2 w-2 bg-blue-500 rounded-full mt-2"></div>
                      <p className="text-sm">Professional tone and business value</p>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="h-2 w-2 bg-blue-500 rounded-full mt-2"></div>
                      <p className="text-sm">Focus on insights and thought leadership</p>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="h-2 w-2 bg-blue-500 rounded-full mt-2"></div>
                      <p className="text-sm">Include relevant hashtags (3-5)</p>
                    </div>
                  </>
                )}
                
                {platform === 'instagram' && (
                  <>
                    <div className="flex items-start gap-2">
                      <div className="h-2 w-2 bg-pink-500 rounded-full mt-2"></div>
                      <p className="text-sm">Visual and engaging language</p>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="h-2 w-2 bg-pink-500 rounded-full mt-2"></div>
                      <p className="text-sm">Use relevant emojis 😊✨</p>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="h-2 w-2 bg-pink-500 rounded-full mt-2"></div>
                      <p className="text-sm">Call to action in
