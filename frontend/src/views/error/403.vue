<template>
  <div class="error-page">
    <h1>403 Forbidden</h1>
    <p>You do not have permission to access this page.</p>
    <el-button type="primary" @click="$router.push('/')">Go Home</el-button>
  </div>
</template>

<style scoped>
.error-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
}
</style>
