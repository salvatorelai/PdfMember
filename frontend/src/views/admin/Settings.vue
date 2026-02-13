<template>
  <div class="settings-container">
    <h2>System Settings</h2>
    <el-card>
      <el-form :model="form" label-width="150px" v-loading="loading">
        <el-divider content-position="left">AI Configuration</el-divider>
        <el-form-item label="AI Base URL">
          <el-input v-model="form.ai_base_url" placeholder="e.g., https://api.openai.com/v1" />
        </el-form-item>
        <el-form-item label="AI API Key">
          <el-input v-model="form.ai_api_key" type="password" show-password placeholder="Enter OpenAI API Key" />
        </el-form-item>
        <el-form-item label="AI Model">
          <el-select 
            v-model="form.ai_model" 
            placeholder="Select or enter model"
            filterable
            allow-create
            default-first-option
          >
            <el-option label="GPT-3.5 Turbo" value="gpt-3.5-turbo" />
            <el-option label="GPT-4" value="gpt-4" />
            <el-option label="GPT-4o" value="gpt-4o" />
            <el-option label="GPT-4o Mini" value="gpt-4o-mini" />
          </el-select>
        </el-form-item>

        <el-divider content-position="left">PDF Processing</el-divider>
        <el-form-item label="Screenshot Pages">
          <el-input-number v-model="form.screenshot_pages" :min="1" :max="10" />
          <div class="help-text">Number of pages to screenshot from the beginning</div>
        </el-form-item>
        <el-form-item label="Specific Indices">
          <el-input v-model="form.screenshot_indices" placeholder="e.g., 0,5,10" />
          <div class="help-text">Comma-separated list of specific page indices (0-based)</div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="saveSettings" :loading="saving">Save Settings</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../../utils/request'

interface SettingsForm {
  ai_api_key: string
  ai_base_url: string
  ai_model: string
  screenshot_pages: number
  screenshot_indices: string
}

const loading = ref(false)
const saving = ref(false)
const form = ref<SettingsForm>({
  ai_api_key: '',
  ai_base_url: '',
  ai_model: 'gpt-3.5-turbo',
  screenshot_pages: 3,
  screenshot_indices: ''
})

const fetchSettings = async () => {
  loading.value = true
  try {
    const response = await request({
      url: '/admin/settings',
      method: 'get'
    })
    
    // Map response to form
    if (Array.isArray(response)) {
      response.forEach((setting: any) => {
        if (setting.key === 'ai_api_key') form.value.ai_api_key = setting.value
        if (setting.key === 'ai_base_url') form.value.ai_base_url = setting.value
        if (setting.key === 'ai_model') form.value.ai_model = setting.value
        if (setting.key === 'screenshot_pages') form.value.screenshot_pages = parseInt(setting.value) || 3
        if (setting.key === 'screenshot_indices') form.value.screenshot_indices = setting.value
      })
    }
  } catch (error) {
    ElMessage.error('Failed to load settings')
  } finally {
    loading.value = false
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    const settings = [
      { key: 'ai_api_key', value: form.value.ai_api_key },
      { key: 'ai_base_url', value: form.value.ai_base_url },
      { key: 'ai_model', value: form.value.ai_model },
      { key: 'screenshot_pages', value: form.value.screenshot_pages.toString() },
      { key: 'screenshot_indices', value: form.value.screenshot_indices }
    ]
    
    await request({
      url: '/admin/settings',
      method: 'put',
      data: settings
    })
    
    ElMessage.success('Settings saved successfully')
  } catch (error) {
    ElMessage.error('Failed to save settings')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchSettings()
})
</script>

<style scoped>
.settings-container {
  padding: 20px;
}
.help-text {
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
  margin-top: 5px;
}
</style>
