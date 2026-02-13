<template>
  <div class="document-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <el-button @click="$router.back()">Back</el-button>
          <span>Document Details</span>
          <div></div> <!-- Spacer -->
        </div>
      </template>
      
      <div v-if="document" class="content">
        <h1 class="title">{{ document.title }}</h1>
        <div class="meta">
          <el-tag v-if="document.category">{{ document.category.name }}</el-tag>
          <span class="time">Uploaded: {{ formatDate(document.created_at) }}</span>
          <span class="views">Views: {{ document.view_count }}</span>
        </div>
        
        <div class="screenshots-section" v-if="document.screenshots && document.screenshots.length > 0">
          <h3>Screenshots</h3>
          <div class="screenshots-list">
             <div 
               v-for="(shot, index) in document.screenshots" 
               :key="index" 
               class="screenshot-item"
             >
               <el-image 
                 :src="shot" 
                 :preview-src-list="document.screenshots"
                 fit="contain"
                 :initial-index="index"
                 class="screenshot-image"
               >
                 <template #error>
                   <div class="image-slot">
                     <el-icon><Picture /></el-icon>
                   </div>
                 </template>
               </el-image>
               <div class="page-label">Page {{ getPageNumber(shot) }}</div>
             </div>
          </div>
        </div>

        <div class="description">
          <h3>Description</h3>
          <p>{{ document.description || 'No description provided.' }}</p>
        </div>
        
        <div class="actions">
          <el-button type="primary" size="large" @click="handleRead">
            Read Document
          </el-button>
          <el-button type="success" size="large" @click="handleDownload" :loading="downloading">
            Download ({{ formatSize(document.file_size) }})
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getDocument, downloadDocument } from '../../api/document'
import type { Document } from '../../api/document'
import { ElMessage } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const document = ref<Document | null>(null)
const loading = ref(false)
const downloading = ref(false)

const getPageNumber = (url: string) => {
  // url format: .../filename_page_1.jpg
  try {
    const match = url.match(/_page_(\d+)\./)
    return match ? match[1] : '?'
  } catch (e) {
    return '?'
  }
}

const fetchDocument = async () => {
  const id = parseInt(route.params.id as string)
  if (!id) return
  
  loading.value = true
  try {
    const res = await getDocument(id)
    document.value = res
  } catch (error) {
    ElMessage.error('Failed to load document')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleRead = () => {
  if (document.value) {
    router.push(`/document/${document.value.id}/read`)
  }
}

const handleDownload = async () => {
  if (!document.value) return
  
  downloading.value = true
  try {
    const res = await downloadDocument(document.value.id)
    let url = res.url
    
    // Handle local paths
    if (url.startsWith('/static')) {
       // In production/dev, this should be the API base URL or static file server
       // Assuming Vite proxy forwards /static to backend, or we prepend backend URL
       // If using Vite proxy (which we are), /static works if we are on the same host
       // But if we are in dev mode, we might need full URL if we want to force download or open
       // Actually, window.open('/static/...') works if proxy is set up.
       // However, to be safe:
       // url = import.meta.env.VITE_API_URL + url // if we had env var
       // For now, rely on Vite proxy
    }
    
    window.open(url, '_blank')
    ElMessage.success('Download started')
  } catch (error: any) {
    // Error handling is done by request interceptor usually, but if we need specific handling:
    if (error.response?.status === 403) {
       // Message already shown by interceptor if configured, but let's be explicit if not
       // ElMessage.error(error.response.data.detail || 'Download failed')
    }
  } finally {
    downloading.value = false
  }
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString()
}

const formatSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

onMounted(() => {
  fetchDocument()
})
</script>

<style scoped>
.document-detail {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  font-size: 24px;
  margin-bottom: 20px;
}
.meta {
  display: flex;
  gap: 20px;
  color: #909399;
  margin-bottom: 30px;
  align-items: center;
}
.description {
  margin-bottom: 40px;
}
.actions {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.screenshots-section {
  margin-bottom: 40px;
}

.screenshots-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-top: 20px;
}

.screenshot-item {
  width: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 1px solid #eee;
  padding: 10px;
  border-radius: 4px;
}

.screenshot-image {
  width: 100%;
  height: 280px;
  background-color: #f5f7fa;
}

.page-label {
  margin-top: 10px;
  color: #606266;
  font-size: 14px;
}

.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: #f5f7fa;
  color: #909399;
  font-size: 30px;
}
</style>
