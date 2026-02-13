<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>PDF Platform Login</h2>
      </template>
      <el-form :model="loginForm" label-width="80px">
        <el-form-item label="Email">
          <el-input v-model="loginForm.username" placeholder="Email or Username" />
        </el-form-item>
        <el-form-item label="Password">
          <el-input v-model="loginForm.password" type="password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading">Login</el-button>
          <el-button @click="handleRegister">Register</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useUserStore } from '../../stores/user'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { register } from '../../api/auth'

const userStore = useUserStore()
const router = useRouter()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const handleLogin = () => {
  loading.value = true
  userStore.login(loginForm)
    .then(() => {
      ElMessage.success('Login success')
      router.push('/')
    })
    .catch(() => {
      loading.value = false
    })
}

const handleRegister = async () => {
  // Simple email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(loginForm.username)) {
    ElMessage.error('Please provide a valid email address for registration')
    return
  }

  try {
    await register({
      email: loginForm.username, // Using username as email for simplicity in this demo, user should provide email
      username: loginForm.username,
      password: loginForm.password
    })
    ElMessage.success('Registration successful, please login')
  } catch (error) {
    // Error handled by request interceptor
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}
.login-card {
  width: 400px;
}
</style>
