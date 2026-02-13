import request from '../utils/request'

export interface Membership {
  id: number
  type: 'free' | 'normal' | 'lifetime'
  download_quota: number
  download_used: number
  expires_at: string | null
}

export function getMyMembership() {
  return request({
    url: '/membership/me',
    method: 'get'
  })
}

export function redeemCode(code: string) {
  return request({
    url: '/membership/redeem',
    method: 'post',
    data: { code }
  })
}
