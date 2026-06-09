<template>
  <div class="not-found-page">
    <div class="not-found-content">
      <h1 class="error-code">404</h1>
      <p class="error-message">页面不存在</p>
      <p class="error-description">抱歉，您访问的页面不存在或已被移除。</p>
      <a-button type="primary" @click="goHome">
        返回首页
      </a-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function goHome() {
  router.push('/')
}
</script>

<style scoped>
.not-found-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #f5f6fa;
}

.not-found-content {
  text-align: center;
}

.error-code {
  font-size: 120px;
  font-weight: 800;
  color: #F5820D;
  margin: 0;
  line-height: 1;
}

.error-message {
  font-size: 24px;
  color: #333;
  margin: 16px 0 8px;
}

.error-description {
  font-size: 14px;
  color: #666;
  margin-bottom: 24px;
}
</style>
