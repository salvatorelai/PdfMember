<template>
  <el-container class="layout-container">
    <el-header class="header">
      <div class="logo">PDF Platform</div>
      <div class="user-info">
        <el-dropdown @command="handleCommand">
          <span class="el-dropdown-link">
            {{ userStore.name || 'User' }}
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-if="isAdmin" command="admin">Admin Dashboard</el-dropdown-item>
              <el-dropdown-item command="membership">Membership</el-dropdown-item>
              <el-dropdown-item command="logout">Logout</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    
    <el-container>
      <el-aside width="200px" class="aside">
        <el-menu
          :default-active="activeCategory"
          class="el-menu-vertical"
          @select="handleCategorySelect"
        >
          <el-menu-item index="">
            <el-icon><Menu /></el-icon>
            <span>All Categories</span>
          </el-menu-item>
          <template v-for="cat in categoryTree" :key="cat.id">
            <el-sub-menu v-if="cat.children && cat.children.length > 0" :index="cat.id.toString()">
              <template #title>
                <el-icon><Folder /></el-icon>
                <span>{{ cat.name }}</span>
              </template>
              <el-menu-item v-for="child in cat.children" :key="child.id" :index="child.id.toString()">
                <span>{{ child.name }}</span>
              </el-menu-item>
            </el-sub-menu>
            <el-menu-item v-else :index="cat.id.toString()">
              <el-icon><Folder /></el-icon>
              <span>{{ cat.name }}</span>
            </el-menu-item>
          </template>
        </el-menu>
      </el-aside>
      
      <el-main class="main">
        <div class="toolbar">
          <el-input
            v-model="searchQuery"
            placeholder="Search documents..."
            style="width: 300px"
            clearable
            @clear="fetchDocuments"
            @keyup.enter="fetchDocuments"
          >
            <template #append>
              <el-button @click="fetchDocuments"><el-icon><Search /></el-icon></el-button>
            </template>
          </el-input>
        </div>
        
        <el-row :gutter="20" v-loading="loading">
          <el-col :span="6" v-for="doc in documents" :key="doc.id" style="margin-bottom: 20px;">
            <el-card :body-style="{ padding: '0px' }" shadow="hover" @click="goToDetail(doc.id)">
              <div class="doc-cover">
                <img 
                  v-if="doc.cover_image" 
                  :src="getCoverUrl(doc.cover_image)" 
                  class="cover-image" 
                  alt="cover" 
                />
                <el-icon v-else :size="50" color="#909399"><DocumentIcon /></el-icon>
              </div>
              <div style="padding: 14px">
                <span class="doc-title">{{ doc.title }}</span>
                <div class="bottom">
                  <time class="time">{{ formatDate(doc.created_at) }}</time>
                  <el-tag size="small" v-if="doc.category">{{ doc.category.name }}</el-tag>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <div class="pagination" v-if="total > 0">
          <el-pagination
            background
            layout="prev, pager, next"
            :total="total"
            :page-size="limit"
            @current-change="handlePageChange"
          />
        </div>
      </el-main>
    </el-container>

    <!-- Upload Dialog -->
    <el-dialog v-model="dialogVisible" title="Upload Document" width="500px">
      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="Category">
          <el-select v-model="uploadForm.category_id" placeholder="Select category">
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Title">
          <el-input v-model="uploadForm.title" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="uploadForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="File">
          <input type="file" @change="handleFileChange" accept="application/pdf" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="handleUpload" :loading="uploading">
            Upload
          </el-button>
        </span>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'
import { getDocuments, getCategories, uploadFile, createDocument } from '../api/document'
import type { Document, Category } from '../api/document'
import { ElMessage } from 'element-plus'
import { ArrowDown, Menu, Folder, Search, Document as DocumentIcon } from '@element-plus/icons-vue'

const userStore = useUserStore()
const router = useRouter()

const isAdmin = computed(() => {
  const roles = userStore.roles.map(r => r.toLowerCase())
  return roles.includes('admin') || roles.includes('super_admin')
})

interface CategoryWithChildren extends Category {
  children?: CategoryWithChildren[]
}

const categories = ref<Category[]>([])
const categoryTree = computed(() => {
  const map = new Map<number, CategoryWithChildren>()
  const roots: CategoryWithChildren[] = []

  // Initialize map with clone to avoid mutating original
  categories.value.forEach(cat => {
    map.set(cat.id, { ...cat, children: [] })
  })

  // Build tree
  categories.value.forEach(cat => {
    const node = map.get(cat.id)!
    if (cat.parent_id) {
      const parent = map.get(cat.parent_id)
      if (parent) {
        parent.children?.push(node)
      } else {
        roots.push(node)
      }
    } else {
      roots.push(node)
    }
  })

  return roots
})

const documents = ref<Document[]>([])
const loading = ref(false)
const activeCategory = ref('')
const searchQuery = ref('')
const page = ref(1)
const limit = ref(12)
const total = ref(0)

const dialogVisible = ref(false)
const uploading = ref(false)
const uploadForm = ref({
  category_id: undefined as number | undefined,
  title: '',
  description: '',
  file: null as File | null
})

const getCoverUrl = (path: string) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  if (path.startsWith('/static')) return path
  // If path starts with /screenshots, prepend /static
  if (path.startsWith('/screenshots')) return `/static${path}`
  // If path is relative like "screenshots/...", prepend /static/
  if (path.startsWith('screenshots')) return `/static/${path}`
  return path
}

const handleCommand = (command: string) => {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  } else if (command === 'membership') {
    router.push('/membership')
  } else if (command === 'admin') {
    router.push('/admin')
  }
}

const fetchCategories = async () => {
  try {
    const res = await getCategories({ all_categories: true })
    categories.value = res
  } catch (error) {
    console.error(error)
  }
}

const fetchDocuments = async () => {
  loading.value = true
  try {
    const res = await getDocuments({
      page: page.value,
      limit: limit.value,
      category_id: activeCategory.value ? parseInt(activeCategory.value) : undefined
    })
    documents.value = res
    // Mock total for now as API might not return it in list (adjust based on actual API response)
    // Assuming API returns { data: [], total: number } or similar
    // If just array, we can't paginate properly without total. 
    // Let's assume the API wrapper handles response.data. 
    // If backend returns list directly, we need to adjust backend to return pagination info.
    // For now, let's assume simple list.
    total.value = 100 // Placeholder
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleCategorySelect = (index: string) => {
  activeCategory.value = index
  page.value = 1
  fetchDocuments()
}

const handlePageChange = (val: number) => {
  page.value = val
  fetchDocuments()
}

const goToDetail = (id: number) => {
  router.push(`/document/${id}`)
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString()
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    uploadForm.value.file = target.files[0]
  }
}

const handleUpload = async () => {
  if (!uploadForm.value.file || !uploadForm.value.category_id) {
    ElMessage.warning('Please select a file and category')
    return
  }
  
  uploading.value = true
  try {
    // 1. Upload file
    const uploadRes = await uploadFile(uploadForm.value.file)
    const { file_path, file_name, file_size } = uploadRes.data
    
    // 2. Create document record
    await createDocument({
      title: uploadForm.value.title || file_name,
      description: uploadForm.value.description,
      category_id: uploadForm.value.category_id,
      file_path,
      file_name,
      file_size,
      status: 'published'
    })
    
    ElMessage.success('Document uploaded successfully')
    dialogVisible.value = false
    fetchDocuments()
    // Reset form
    uploadForm.value = { category_id: undefined, title: '', description: '', file: null }
  } catch (error) {
    ElMessage.error('Upload failed')
    console.error(error)
  } finally {
    uploading.value = false
  }
}

onMounted(() => {
  fetchCategories()
  fetchDocuments()
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.logo {
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
}

.aside {
  background-color: #fff;
  border-right: 1px solid #dcdfe6;
}

.main {
  background-color: #f5f7fa;
}

.toolbar {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-end;
}

.doc-cover {
  height: 160px;
  background-color: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background-color: #f5f7fa;
}

.doc-title {
  font-size: 16px;
  font-weight: bold;
  display: block;
  margin-bottom: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.time {
  font-size: 13px;
  color: #999;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
}
</style>
