import request from '../utils/request'
import type { User } from './auth'
import type { Document } from './document'

export interface DashboardStats {
  user_count: number
  document_count: number
  download_count: number
  revenue: number
}

export function getDashboardStats() {
  return request({
    url: '/admin/stats',
    method: 'get'
  })
}

// User Management
export function getUsers(params: any) {
  return request({
    url: '/admin/users',
    method: 'get',
    params
  })
}

export function updateUser(id: number, data: any) {
  return request({
    url: `/admin/users/${id}`,
    method: 'put',
    data
  })
}

// Document Management
export function getAdminDocuments(params: any) {
  return request({
    url: '/admin/documents',
    method: 'get',
    params
  })
}

export function updateDocument(id: number, data: any) {
  return request({
    url: `/admin/documents/${id}`,
    method: 'put',
    data
  })
}

export function deleteDocument(id: number) {
  return request({
    url: `/admin/documents/${id}`,
    method: 'delete'
  })
}

export function analyzeDocument(id: number) {
  return request({
    url: `/admin/documents/${id}/analyze`,
    method: 'post'
  })
}
