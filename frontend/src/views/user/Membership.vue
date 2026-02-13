<template>
  <div class="membership-container">
    <el-card class="membership-card">
      <template #header>
        <div class="card-header">
          <span>My Membership</span>
        </div>
      </template>
      
      <div v-loading="loading">
        <div v-if="membership" class="info-section">
          <div class="status-item">
            <span class="label">Type:</span>
            <el-tag :type="getMembershipTagType(membership.type)" size="large">
              {{ membership.type.toUpperCase() }}
            </el-tag>
          </div>
          
          <div class="status-item">
            <span class="label">Status:</span>
            <span :class="{ 'active': isMembershipActive, 'expired': !isMembershipActive }">
              {{ isMembershipActive ? 'Active' : 'Expired' }}
            </span>
          </div>

          <div class="status-item" v-if="membership.expires_at">
            <span class="label">Expires At:</span>
            <span>{{ formatDate(membership.expires_at) }}</span>
          </div>
          <div class="status-item" v-else-if="membership.type === 'lifetime'">
             <span class="label">Expires At:</span>
             <span>Never</span>
          </div>

          <div class="status-item">
            <span class="label">Download Quota:</span>
            <el-progress 
              :percentage="quotaPercentage" 
              :format="quotaFormat"
              :status="quotaPercentage >= 100 ? 'exception' : 'success'"
              style="width: 300px"
            />
          </div>
        </div>

        <el-divider />

        <div class="redeem-section">
          <h3>Redeem Membership Code</h3>
          <el-form :inline="true" @submit.prevent>
            <el-form-item>
              <el-input 
                v-model="redeemCodeInput" 
                placeholder="Enter code (e.g. VIP-2024)" 
                style="width: 300px"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleRedeem" :loading="redeeming">
                Redeem
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getMyMembership, redeemCode } from '../../api/membership'
import type { Membership } from '../../api/membership'
import { ElMessage } from 'element-plus'

const membership = ref<Membership | null>(null)
const loading = ref(false)
const redeeming = ref(false)
const redeemCodeInput = ref('')

const fetchMembership = async () => {
  loading.value = true
  try {
    const res = await getMyMembership()
    membership.value = res.data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleRedeem = async () => {
  if (!redeemCodeInput.value) {
    ElMessage.warning('Please enter a code')
    return
  }
  
  redeeming.value = true
  try {
    const res = await redeemCode(redeemCodeInput.value)
    membership.value = res.data
    ElMessage.success('Code redeemed successfully!')
    redeemCodeInput.value = ''
  } catch (error) {
    // Error handled by interceptor
  } finally {
    redeeming.value = false
  }
}

const isMembershipActive = computed(() => {
  if (!membership.value) return false
  if (membership.value.type === 'lifetime') return true
  if (!membership.value.expires_at) return true // Free plan no expiry usually? Or check logic.
  // Actually free plan has expires_at=None usually? 
  // Let's assume if expires_at is null, it's valid unless logic says otherwise.
  // But Free plan is always valid.
  if (membership.value.type === 'free') return true
  
  return new Date(membership.value.expires_at) > new Date()
})

const quotaPercentage = computed(() => {
  if (!membership.value) return 0
  if (membership.value.download_quota === 0) return 100
  if (membership.value.download_quota > 99999) return 0 // Unlimited-ish
  return Math.min(100, Math.round((membership.value.download_used / membership.value.download_quota) * 100))
})

const quotaFormat = () => {
  if (!membership.value) return ''
  if (membership.value.download_quota > 99999) return 'Unlimited'
  return `${membership.value.download_used} / ${membership.value.download_quota}`
}

const getMembershipTagType = (type: string) => {
  const map: Record<string, string> = {
    free: 'info',
    normal: 'primary',
    lifetime: 'warning'
  }
  return map[type] || 'info'
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString() + ' ' + new Date(dateStr).toLocaleTimeString()
}

onMounted(() => {
  fetchMembership()
})
</script>

<style scoped>
.membership-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}
.card-header {
  font-weight: bold;
  font-size: 18px;
}
.info-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.status-item {
  display: flex;
  align-items: center;
  gap: 20px;
}
.label {
  font-weight: bold;
  width: 150px;
  color: #606266;
}
.active {
  color: #67c23a;
  font-weight: bold;
}
.expired {
  color: #f56c6c;
  font-weight: bold;
}
.redeem-section {
  margin-top: 30px;
}
</style>
