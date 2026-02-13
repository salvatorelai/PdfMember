<template>
  <div class="download-container">
    <el-card class="box-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <h2>Secure Download</h2>
        </div>
      </template>
      
      <div v-if="error" class="error-msg">
        <el-result icon="error" title="Invalid or Expired Link" sub-title="Please contact the administrator." />
      </div>
      
      <div v-else-if="info">
        <div class="file-info">
          <h3>{{ info.document_title }}</h3>
          <p>Expires at: {{ new Date(info.expires_at).toLocaleString() }}</p>
        </div>

        <div v-if="info.requires_password" class="password-section">
          <el-input 
            v-model="password" 
            placeholder="Enter Password" 
            type="password" 
            show-password
            @keyup.enter="handleDownload"
          />
        </div>

        <div class="action-section">
          <el-button type="primary" size="large" @click="handleDownload" :loading="downloading">
            Download File
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import request from '../utils/request'
import { ElMessage } from 'element-plus'

const route = useRoute()
const token = route.params.token as string

const loading = ref(true)
const downloading = ref(false)
const error = ref(false)
const info = ref<any>(null)
const password = ref('')

const checkToken = async () => {
  try {
    const res = await request({
      url: `/documents/download-token/${token}`,
      method: 'get'
    })
    info.value = res
  } catch (err) {
    error.value = true
  } finally {
    loading.value = false
  }
}

const handleDownload = async () => {
  if (info.value.requires_password && !password.value) {
    ElMessage.warning('Password is required')
    return
  }

  downloading.value = true
  try {
    const res = await request({
      url: `/documents/download-token/${token}`,
      method: 'post',
      data: { password: password.value }
    })
    
    // Download logic
    // Backend returns { url: "static/uploads/..." }
    // We need to prepend base URL if it's relative
    const fileUrl = import.meta.env.VITE_API_URL 
      ? `${import.meta.env.VITE_API_URL}/${res.url}`
      : `/api/v1/${res.url}` // Fallback approximation, ideally backend returns full URL or proxy handles it
      
    // Actually, backend returns file_path "static/uploads/..."
    // Nginx serves /static/ -> backend/static/
    // So if I access http://localhost:8080/static/uploads/..., it should work if Nginx is configured.
    // Let's assume standard static serving.
    
    // Better: use window.open
    let downloadUrl = res.url
    if (!downloadUrl.startsWith('http') && !downloadUrl.startsWith('/')) {
      downloadUrl = `/${downloadUrl}`
    }
    window.open(downloadUrl, '_blank')
    
    ElMessage.success('Download started')
  } catch (err) {
    ElMessage.error('Invalid password or expired token')
  } finally {
    downloading.value = false
  }
}

onMounted(() => {
  if (token) {
    checkToken()
  } else {
    error.value = true
    loading.value = false
  }
})
</script>

<style scoped>
.download-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}
.box-card {
  width: 400px;
}
.file-info {
  text-align: center;
  margin-bottom: 20px;
}
.password-section {
  margin-bottom: 20px;
}
.action-section {
  text-align: center;
}
</style>
