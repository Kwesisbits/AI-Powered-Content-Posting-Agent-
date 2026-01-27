import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date) {
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function truncateText(text: string, length: number = 100) {
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}

export function getStatusColor(status: string) {
  switch (status.toLowerCase()) {
    case 'draft':
    case 'pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'approved':
    case 'published':
    case 'success':
      return 'bg-green-100 text-green-800'
    case 'rejected':
    case 'failed':
    case 'cancelled':
      return 'bg-red-100 text-red-800'
    case 'scheduled':
      return 'bg-blue-100 text-blue-800'
    case 'changes_requested':
      return 'bg-orange-100 text-orange-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

export function getPlatformColor(platform: string) {
  switch (platform.toLowerCase()) {
    case 'linkedin':
      return 'bg-blue-500 text-white'
    case 'instagram':
      return 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
    case 'twitter':
      return 'bg-sky-500 text-white'
    default:
      return 'bg-gray-500 text-white'
  }
}
