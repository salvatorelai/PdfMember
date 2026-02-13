<template>
  <div class="app-container">
    <div class="header">
      <h2>Category Management</h2>
      <el-button type="primary" @click="handleAdd">Add Category</el-button>
    </div>
    
    <el-table v-loading="loading" :data="categories" border style="width: 100%" row-key="id" default-expand-all>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="Name" />
      <el-table-column prop="slug" label="Slug" />
      <el-table-column prop="description" label="Description" />
      <el-table-column label="Parent" width="120">
        <template #default="scope">
          {{ getCategoryName(scope.row.parent_id) }}
        </template>
      </el-table-column>
      <el-table-column prop="sort_order" label="Sort Order" width="100" />
      <el-table-column label="Actions" width="200">
        <template #default="scope">
          <el-button size="small" @click="handleEdit(scope.row)">Edit</el-button>
          <el-button size="small" type="danger" @click="handleDelete(scope.row)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogType === 'add' ? 'Add Category' : 'Edit Category'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="Name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="Slug">
          <el-input v-model="form.slug" />
        </el-form-item>
        <el-form-item label="Parent">
          <el-select v-model="form.parent_id" placeholder="Select Parent Category" clearable style="width: 100%">
            <el-option
              v-for="item in categories"
              :key="item.id"
              :label="item.name"
              :value="item.id"
              :disabled="item.id === form.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
        <el-form-item label="Sort Order">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">Confirm</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getCategories, createCategory, updateCategory, deleteCategory } from '../../api/document'
import type { Category } from '../../api/document'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const categories = ref<Category[]>([])
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const submitting = ref(false)

const form = ref({
  id: undefined as number | undefined,
  name: '',
  slug: '',
  description: '',
  parent_id: undefined as number | undefined,
  sort_order: 0
})

const getCategoryName = (id: number) => {
  if (!id) return '-'
  const cat = categories.value.find(c => c.id === id)
  return cat ? cat.name : id
}

const fetchCategories = async () => {
  loading.value = true
  try {
    const res = await getCategories({ all_categories: true })
    categories.value = res
  } catch (error) {
    ElMessage.error('Failed to load categories')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogType.value = 'add'
  form.value = { id: undefined, name: '', slug: '', description: '', parent_id: undefined, sort_order: 0 }
  dialogVisible.value = true
}

const handleEdit = (row: Category) => {
  dialogType.value = 'edit'
  form.value = { 
    id: row.id, 
    name: row.name, 
    slug: row.slug, 
    description: row.description || '', 
    parent_id: row.parent_id,
    sort_order: (row as any).sort_order || 0 
  }
  dialogVisible.value = true
}

const handleDelete = (row: Category) => {
  ElMessageBox.confirm('Are you sure to delete this category?', 'Warning', {
    type: 'warning'
  }).then(async () => {
    try {
      await deleteCategory(row.id)
      ElMessage.success('Deleted successfully')
      fetchCategories()
    } catch (error) {
      ElMessage.error('Delete failed')
    }
  })
}

const handleSubmit = async () => {
  if (!form.value.name || !form.value.slug) {
    ElMessage.warning('Name and Slug are required')
    return
  }

  submitting.value = true
  try {
    if (dialogType.value === 'add') {
      await createCategory(form.value)
      ElMessage.success('Created successfully')
    } else {
      await updateCategory(form.value.id!, form.value)
      ElMessage.success('Updated successfully')
    }
    dialogVisible.value = false
    fetchCategories()
  } catch (error) {
    ElMessage.error('Operation failed')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.app-container {
  padding: 20px;
}
.header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>