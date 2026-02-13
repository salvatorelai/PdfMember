<template>
  <div class="dashboard-container" v-loading="loading">
    <h2>Admin Dashboard</h2>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>Total Users</template>
          <div class="stat-value">{{ stats.user_count }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>Total Documents</template>
          <div class="stat-value">{{ stats.document_count }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>Total Downloads</template>
          <div class="stat-value">{{ stats.download_count }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>Revenue (Lifetime)</template>
          <div class="stat-value">${{ stats.revenue }}</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getDashboardStats } from '../../api/admin'
import type { DashboardStats } from '../../api/admin'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const stats = ref<DashboardStats>({
  user_count: 0,
  document_count: 0,
  download_count: 0,
  revenue: 0
})

const fetchStats = async () => {
  loading.value = true
  try {
    const res = await getDashboardStats()
    stats.value = res
  } catch (error) {
    ElMessage.error('Failed to load dashboard stats')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}
.stat-value {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  padding: 10px 0;
}
</style>
