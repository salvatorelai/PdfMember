import { defineStore } from 'pinia'
import { login, getInfo } from '../api/auth'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const name = ref('')
  const avatar = ref('')
  const roles = ref<string[]>([])

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function loginAction(userInfo: any) {
    return new Promise<void>((resolve, reject) => {
      login(userInfo).then((response: any) => {
        const { access_token } = response
        setToken(access_token)
        resolve()
      }).catch(error => {
        reject(error)
      })
    })
  }

  function getUserInfo() {
    return new Promise((resolve, reject) => {
      getInfo().then((data: any) => {
        if (!data) {
          reject('Verification failed, please Login again.')
          return
        }
        const { username, role } = data
        name.value = username
        roles.value = [role]
        resolve(data)
      }).catch(error => {
        reject(error)
      })
    })
  }

  function logout() {
    token.value = ''
    roles.value = []
    localStorage.removeItem('token')
  }

  return { token, name, avatar, roles, login: loginAction, getUserInfo, logout }
})
