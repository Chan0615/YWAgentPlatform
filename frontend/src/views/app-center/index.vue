<template>
  <div class="app-center-page">
    <!-- Page Header -->
    <div class="page-header">
      <h2 class="page-title">应用中心</h2>
      <a-input-search
        v-model:value="searchText"
        placeholder="搜索应用名称"
        style="width: 260px"
        allow-clear
        class="search-input"
      />
    </div>

    <!-- App Grid -->
    <a-spin :spinning="loading">
      <!-- Skeleton Loading -->
      <div v-if="loading" class="app-grid">
        <div v-for="i in 8" :key="i" class="app-card app-card--skeleton">
          <div class="card-header-skeleton"></div>
          <div class="card-body-skeleton">
            <a-skeleton :paragraph="{ rows: 2 }" active />
          </div>
        </div>
      </div>

      <!-- App Cards -->
      <div v-else-if="filteredApps.length > 0" class="app-grid">
        <div
          v-for="(app, index) in filteredApps"
          :key="app.id"
          class="app-card"
        >
          <!-- Card Gradient Header -->
          <div class="card-header" :style="{ background: getGradient(index) }">
            <div class="card-avatar">
              {{ app.name.charAt(0) }}
            </div>
          </div>

          <!-- Card Body -->
          <div class="card-body">
            <div class="card-info">
              <h3 class="app-name">{{ app.name }}</h3>
              <p class="app-desc">{{ app.description || '暂无描述' }}</p>
            </div>
            <div class="card-footer">
              <a-tag :color="app.status === 1 ? 'green' : 'red'" size="small">
                {{ app.status === 1 ? '运行中' : '已停用' }}
              </a-tag>
              <a class="enter-btn" @click="openApp(app)">
                进入应用
                <RightOutlined style="font-size: 11px" />
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <a-empty description="暂无可访问的应用">
          <template #image>
            <AppstoreOutlined style="font-size: 64px; color: #ddd" />
          </template>
        </a-empty>
      </div>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { AppstoreOutlined, RightOutlined } from '@ant-design/icons-vue'
import { useAppStore, type AppInfo } from '@/store/app'
import { useUserStore } from '@/store/user'

const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

const searchText = ref('')
const loading = ref(false)

// Gradient palette for card headers
const gradients = [
  'linear-gradient(135deg, #F5820D 0%, #FF6B35 100%)',
  'linear-gradient(135deg, #1890ff 0%, #36cfc9 100%)',
  'linear-gradient(135deg, #722ed1 0%, #b37feb 100%)',
  'linear-gradient(135deg, #52c41a 0%, #95de64 100%)',
  'linear-gradient(135deg, #eb2f96 0%, #ff85c0 100%)',
  'linear-gradient(135deg, #faad14 0%, #ffd666 100%)',
  'linear-gradient(135deg, #13c2c2 0%, #5cdbd3 100%)',
  'linear-gradient(135deg, #2f54eb 0%, #85a5ff 100%)',
]

function getGradient(index: number): string {
  return gradients[index % gradients.length]
}

// Filter apps by permission and search
const filteredApps = computed(() => {
  let apps = appStore.applications.filter((app) => {
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
        app.description?.toLowerCase().includes(keyword)
    )
  }

  return apps
})

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
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ===== Page Header ===== */
.page-header {
  background: #fff;
  border-radius: 10px;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;
}

.search-input :deep(.ant-input-search-button) {
  background: #F5820D;
  border-color: #F5820D;
}

.search-input :deep(.ant-input:hover),
.search-input :deep(.ant-input:focus) {
  border-color: #F5820D;
}

.search-input :deep(.ant-input-wrapper:hover .ant-input),
.search-input :deep(.ant-input-affix-wrapper:hover) {
  border-color: #F5820D;
}

/* ===== App Grid ===== */
.app-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

@media (max-width: 1400px) {
  .app-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 992px) {
  .app-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 576px) {
  .app-grid {
    grid-template-columns: 1fr;
  }
}

/* ===== App Card ===== */
.app-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.app-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

/* Card Header - Gradient Area */
.card-header {
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.card-avatar {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
  color: #fff;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

/* Card Body */
.card-body {
  padding: 16px 20px 20px;
}

.card-info {
  margin-bottom: 14px;
}

.app-name {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 6px;
}

.app-desc {
  font-size: 13px;
  color: #999;
  margin: 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: 39px;
}

/* Card Footer */
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid #f5f5f5;
}

.enter-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #F5820D;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.enter-btn:hover {
  color: #d4700b;
  gap: 6px;
}

/* ===== Skeleton ===== */
.app-card--skeleton {
  pointer-events: none;
}

.card-header-skeleton {
  height: 100px;
  background: linear-gradient(135deg, #f0f0f0 0%, #e8e8e8 100%);
}

.card-body-skeleton {
  padding: 16px 20px;
}

/* ===== Empty State ===== */
.empty-state {
  background: #fff;
  border-radius: 10px;
  padding: 80px 24px;
  text-align: center;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}
</style>
