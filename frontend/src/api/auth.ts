import request from '../utils/request'

export interface User {
  id: number
  username: string
  email: string
  role: string
  status: string
  created_at: string
}

export function login(data: any) {
  return request({
    url: '/auth/login/access-token',
    method: 'post',
    data,
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

export function register(data: any) {
  return request({
    url: '/auth/register',
    method: 'post',
    data
  })
}

export function getInfo() {
  return request({
    url: '/auth/test-token', // Using test-token to get current user info for now
    method: 'post'
  })
}
