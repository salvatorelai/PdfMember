<template>
  <div class="app-container">
    <div class="header">
      <h2>User Management</h2>
    </div>
    
    <el-table v-loading="loading" :data="users" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="Username" />
      <el-table-column prop="email" label="Email" />
      <el-table-column prop="role" label="Role">
        <template #default="scope">
          <el-tag :type="scope.row.role === 'admin' ? 'danger' : 'success'">
            {{ scope.row.role }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="Status">
        <template #default="scope">
          <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'">
            {{ scope.row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Actions" width="200">
        <template #default="scope">
          <el-button 
            v-if="scope.row.status === 'active'"
            size="small" 
            type="warning" 
            @click="handleStatus(scope.row, 'banned')"
          >
            Ban
          </el-button>
          <el-button 
            v-else
            size="small" 
            type="success" 
            @click="handleStatus(scope.row, 'active')"
          >
            Activate
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getUsers, updateUser } from '../../api/admin'
import type { User } from '../../api/auth'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const users = ref<User[]>([])

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await getUsers({ limit: 100 })
    users.value = res
  } catch (error) {
    ElMessage.error('Failed to load users')
  } finally {
    loading.value = false
  }
}

const handleStatus = async (user: User, status: string) => {
  try {
    await updateUser(user.id, { status })
    ElMessage.success('User updated')
    fetchUsers()
  } catch (error) {
    ElMessage.error('Failed to update user')
  }
}

onMounted(() => {
  fetchUsers()
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
