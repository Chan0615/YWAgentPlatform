<template>
  <div class="app-container-page">
    <div v-if="loading" class="loading-wrapper">
      <a-spin size="large" tip="加载应用中..." />
    </div>
    <div v-else-if="appUrl" class="iframe-wrapper">
      <div class="iframe-header">
        <a-button type="link" @click="goBack">
          <template #icon><ArrowLeftOutlined /></template>
          返回应用中心
        </a-button>
        <span class="app-title">{{ appName }}</span>
        <a-button type="link" @click="reloadIframe">
          <template #icon><ReloadOutlined /></template>
          刷新
        </a-button>
      </div>
      <iframe
        ref="iframeRef"
        :src="iframeSrc"
        class="app-iframe"
        frameborder="0"
        allowfullscreen
        @load="onIframeLoad"
      />
    </div>
    <a-result v-else status="404" title="应用未找到" sub-title="请检查应用配置">
      <template #extra>
        <a-button type="primary" @click="goBack">返回应用中心</a-button>
      </template>
    </a-result>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeftOutlined, ReloadOutlined } from '@ant-design/icons-vue'
import { getApplicationDetailApi } from '@/api/application'
import { getToken } from '@/utils/auth'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const appUrl = ref('')
const appName = ref('')
const iframeRef = ref<HTMLIFrameElement | null>(null)

const iframeSrc = ref('')

function goBack() {
  router.push('/app-center')
}

function reloadIframe() {
  if (iframeRef.value) {
    iframeRef.value.src = iframeSrc.value
  }
}

function onIframeLoad() {
  loading.value = false
}

onMounted(async () => {
  const appId = Number(route.params.appId)
  if (!appId) {
    loading.value = false
    return
  }

  try {
    const app = await getApplicationDetailApi(appId)
    appUrl.value = app.url
    appName.value = app.name

    // Append token as query parameter for SSO
    const separator = app.url.includes('?') ? '&' : '?'
    iframeSrc.value = `${app.url}${separator}token=${encodeURIComponent(getToken())}`
  } catch {
    appUrl.value = ''
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.app-container-page {
  height: calc(100vh - 64px - 70px - 48px);
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

.loading-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.iframe-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.iframe-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.app-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.app-iframe {
  flex: 1;
  width: 100%;
  border: none;
}
</style>
