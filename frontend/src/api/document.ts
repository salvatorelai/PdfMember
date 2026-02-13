import request from '../utils/request'

export interface Category {
  id: number
  name: string
  slug: string
  description?: string
  parent_id?: number
  icon?: string
}

export interface Document {
  id: number
  title: string
  description?: string
  category_id: number
  category?: Category
  file_path: string
  file_name: string
  file_size: number
  page_count?: number
  view_count: number
  download_count: number
  status: string
  created_at: string
  updated_at: string
  cover_image?: string
  screenshots?: string[]
  tags?: any[]
}

export interface DocumentQuery {
  page?: number
  limit?: number
  category_id?: number
  status?: string
}

export function getDocuments(query: DocumentQuery) {
  return request({
    url: '/documents/',
    method: 'get',
    params: {
      skip: ((query.page || 1) - 1) * (query.limit || 10),
      limit: query.limit || 10,
      category_id: query.category_id,
      status: query.status
    }
  })
}

export function getDocument(id: number) {
  return request({
    url: `/documents/${id}`,
    method: 'get'
  })
}

export function getCategories(params?: any) {
  return request({
    url: '/documents/categories',
    method: 'get',
    params
  })
}

export function createCategory(data: any) {
  return request({
    url: '/documents/categories',
    method: 'post',
    data
  })
}

export function updateCategory(id: number, data: any) {
  return request({
    url: `/documents/categories/${id}`,
    method: 'put',
    data
  })
}

export function deleteCategory(id: number) {
  return request({
    url: `/documents/categories/${id}`,
    method: 'delete'
  })
}

export function uploadFile(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/documents/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function createDocument(data: any) {
  return request({
    url: '/documents/',
    method: 'post',
    data
  })
}

export function downloadDocument(id: number) {
  return request({
    url: `/documents/${id}/download`,
    method: 'get'
  })
}
