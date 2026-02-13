<template>
  <div class="app-container">
    <div class="header" style="display: flex; justify-content: space-between; align-items: center;">
      <h2>Document Management</h2>
      <el-button type="primary" @click="openUploadDialog">Batch Upload</el-button>
    </div>
    
    <el-table v-loading="loading" :data="documents" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="title" label="Title" min-width="200" show-overflow-tooltip />
      <el-table-column prop="category.name" label="Category" width="120" />
      <el-table-column prop="status" label="Status" width="100">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ scope.row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="Created At" width="180">
        <template #default="scope">
          {{ new Date(scope.row.created_at).toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column label="Actions" width="350">
        <template #default="scope">
          <el-button 
            size="small" 
            type="info" 
            @click="handleAnalyze(scope.row)"
            :loading="analyzingId === scope.row.id"
          >
            Make
          </el-button>
          <el-button 
            size="small" 
            type="primary" 
            @click="handleShare(scope.row)"
          >
            Share
          </el-button>
          <el-button 
            v-if="scope.row.status === 'draft'"
            size="small" 
            type="success" 
            :disabled="!scope.row.screenshots?.length || !scope.row.description"
            title="Screenshots and description required to publish"
            @click="handleStatus(scope.row, 'published')"
          >
            Publish
          </el-button>
          <el-button 
            v-if="scope.row.status === 'published'"
            size="small" 
            type="warning" 
            @click="handleStatus(scope.row, 'draft')"
          >
            Unpublish
          </el-button>
          <el-button 
            size="small" 
            type="danger" 
            @click="handleDelete(scope.row)"
          >
            Delete
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Upload Dialog -->
    <el-dialog v-model="uploadVisible" title="Batch Upload" width="500px">
      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="Category">
          <el-select v-model="uploadForm.category_id" placeholder="Select category" style="width: 100%">
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Files">
          <input type="file" multiple @change="handleFileChange" accept="application/pdf" />
          <div style="font-size: 12px; color: #999; margin-top: 5px;">
            Supported: PDF only. Click 'Make' after upload to generate screenshots & summary.
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadVisible = false">Cancel</el-button>
          <el-button type="primary" @click="handleBatchUpload" :loading="uploading">
            Upload
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Share Dialog -->
    <el-dialog v-model="shareVisible" title="Secure Share" width="500px">
      <div v-if="!shareResult">
        <el-form label-width="120px">
          <el-form-item label="Expiry (Minutes)">
            <el-input-number v-model="shareForm.expires_in_minutes" :min="1" />
          </el-form-item>
          <el-form-item label="Password">
            <el-input v-model="shareForm.password" placeholder="Leave empty for auto-generated" />
          </el-form-item>
        </el-form>
      </div>
      <div v-else>
        <el-alert type="success" :closable="false" title="Link Generated Successfully" />
        <div style="margin-top: 20px;">
          <p><strong>URL:</strong> <a :href="shareResult.url" target="_blank">{{ shareResult.url }}</a></p>
          <p><strong>Password:</strong> {{ shareResult.password }}</p>
          <p><strong>Expires At:</strong> {{ new Date(shareResult.expires_at).toLocaleString() }}</p>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <div v-if="!shareResult">
            <el-button @click="shareVisible = false">Cancel</el-button>
            <el-button type="primary" @click="generateShareLink" :loading="sharing">
              Generate
            </el-button>
          </div>
          <div v-else>
            <el-button type="primary" @click="shareVisible = false">Close</el-button>
          </div>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { getAdminDocuments, updateDocument, deleteDocument, analyzeDocument } from '../../api/admin'
import { getCategories } from '../../api/document'
import request from '../../utils/request'
import type { Document, Category } from '../../api/document'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const documents = ref<Document[]>([])
const analyzingId = ref<number | null>(null)

// Upload State
const uploadVisible = ref(false)
const uploading = ref(false)
const categories = ref<Category[]>([])
const uploadForm = reactive({
  category_id: undefined as number | undefined,
  files: [] as File[]
})

// Share State
const shareVisible = ref(false)
const sharing = ref(false)
const currentDoc = ref<Document | null>(null)
const shareForm = reactive({
  expires_in_minutes: 60,
  password: ''
})
const shareResult = ref<any>(null)

const fetchDocuments = async () => {
  loading.value = true
  try {
    const res = await getAdminDocuments({ limit: 100 })
    documents.value = res
  } catch (error) {
    ElMessage.error('Failed to load documents')
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const res = await getCategories({ all_categories: 'true' })
    categories.value = res
  } catch (error) {
    console.error(error)
  }
}

const openUploadDialog = () => {
  uploadVisible.value = true
  fetchCategories()
}

const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files) {
    uploadForm.files = Array.from(target.files)
  }
}

const handleBatchUpload = async () => {
  if (!uploadForm.category_id || uploadForm.files.length === 0) {
    ElMessage.warning('Please select category and files')
    return
  }
  
  uploading.value = true
  const formData = new FormData()
  formData.append('category_id', uploadForm.category_id.toString())
  uploadForm.files.forEach(file => {
    formData.append('files', file)
  })
  
  try {
    const res = await request({
      url: '/admin/upload/batch',
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    ElMessage.success(`Uploaded ${res.success} files successfully`)
    uploadVisible.value = false
    fetchDocuments()
    // Reset
    uploadForm.category_id = undefined
    uploadForm.files = []
  } catch (error) {
    ElMessage.error('Upload failed')
  } finally {
    uploading.value = false
  }
}

const handleAnalyze = async (doc: Document) => {
  analyzingId.value = doc.id
  try {
    await analyzeDocument(doc.id)
    ElMessage.success('Analysis completed')
    fetchDocuments()
  } catch (error) {
    ElMessage.error('Analysis failed')
  } finally {
    analyzingId.value = null
  }
}

const handleShare = (doc: Document) => {
  currentDoc.value = doc
  shareVisible.value = true
  shareResult.value = null
  shareForm.expires_in_minutes = 60
  shareForm.password = ''
}

const generateShareLink = async () => {
  if (!currentDoc.value) return
  
  sharing.value = true
  try {
    const res = await request({
      url: `/admin/documents/${currentDoc.value.id}/secure-link`,
      method: 'post',
      data: shareForm
    })
    // Prepend base URL to result url
    res.url = window.location.origin + res.url
    shareResult.value = res
  } catch (error) {
    ElMessage.error('Failed to generate link')
  } finally {
    sharing.value = false
  }
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    published: 'success',
    draft: 'info',
    archived: 'warning'
  }
  return map[status] || 'info'
}

const handleStatus = async (doc: Document, status: string) => {
  try {
    await updateDocument(doc.id, { status })
    ElMessage.success('Document updated')
    fetchDocuments()
  } catch (error) {
    ElMessage.error('Failed to update document')
  }
}

const handleDelete = (doc: Document) => {
  ElMessageBox.confirm(
    'Are you sure to delete this document?',
    'Warning',
    {
      confirmButtonText: 'OK',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        await deleteDocument(doc.id)
        ElMessage.success('Delete completed')
        fetchDocuments()
      } catch (error) {
        ElMessage.error('Delete failed')
      }
    })
    .catch(() => {
      ElMessage.info('Delete canceled')
    })
}

onMounted(() => {
  fetchDocuments()
})
</script>

<style scoped>
.app-container {
  padding: 20px;
}
.header {
  margin-bottom: 20px;
}
</style>
