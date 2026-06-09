<template>
  <div class="app-center-page">
    <a-page-header title="应用中心" sub-title="管理和访问所有注册的应用">
      <template #extra>
        <a-input-search
          v-model:value="searchText"
          placeholder="搜索应用"
          style="width: 250px"
          allow-clear
        />
      </template>
    </a-page-header>

    <a-spin :spinning="loading">
      <div v-if="filteredApps.length > 0" class="app-grid">
        <a-card
          v-for="app in filteredApps"
          :key="app.id"
          hoverable
          class="app-card"
          @click="openApp(app)"
        >
          <template #cover>
            <div class="app-icon-wrapper">
              <AppstoreOutlined class="app-icon" />
            </div>
          </template>
          <a-card-meta :title="app.name" :description="app.description">
            <template #avatar>
              <a-avatar
                :style="{ backgroundColor: getAvatarColor(app.code) }"
              >
                {{ app.name.charAt(0) }}
              </a-avatar>
            </template>
          </a-card-meta>
          <div class="app-status">
            <a-tag :color="app.status === 1 ? 'green' : 'red'">
              {{ app.status === 1 ? '正常' : '停用' }}
            </a-tag>
          </div>
        </a-card>
      </div>
      <a-empty v-else description="暂无可访问的应用" />
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { AppstoreOutlined } from '@ant-design/icons-vue'
import { useAppStore, type AppInfo } from '@/store/app'
import { useUserStore } from '@/store/user'

const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

const searchText = ref('')
const loading = ref(false)

const filteredApps = computed(() => {
  let apps = appStore.applications.filter((app) => {
    // Permission check: only show apps the user has access to
    if (app.permission && !userStore.hasPermission(app.permission)) {
      return false
    }
    return app.status === 1
  })

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    apps = apps.filter(
      (app) =>
        app.name.toLowerCase().includes(keyword) ||
        app.description.toLowerCase().includes(keyword)
    )
  }

  return apps
})

const colors = ['#1890ff', '#52c41a', '#722ed1', '#faad14', '#eb2f96', '#13c2c2']

function getAvatarColor(code: string): string {
  const index = code.charCodeAt(0) % colors.length
  return colors[index]
}

function openApp(app: AppInfo) {
  router.push(`/app-container/${app.id}`)
}

onMounted(async () => {
  loading.value = true
  try {
    await appStore.fetchApplications()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.app-center-page {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
}

.app-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  padding: 16px 0;
}

.app-card {
  border-radius: 8px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.app-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.app-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 80px;
  background: linear-gradient(135deg, #f0f5ff 0%, #e6f7ff 100%);
}

.app-icon {
  font-size: 36px;
  color: #1890ff;
}

.app-status {
  margin-top: 12px;
}
</style>
