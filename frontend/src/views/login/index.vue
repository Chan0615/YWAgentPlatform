<template>
  <div class="login-page">
    <!-- Left Illustration Area -->
    <div class="login-left">
      <div class="left-decoration">
        <div class="deco-circle deco-circle-1"></div>
        <div class="deco-circle deco-circle-2"></div>
        <div class="deco-circle deco-circle-3"></div>
        <div class="deco-dots"></div>
      </div>
      <div class="left-content">
        <h1 class="brand-name">YW.OPS</h1>
        <p class="brand-subtitle">统一运维管理平台</p>
        <p class="brand-desc">高效管理多系统 · 统一认证入口 · 全面审计追踪</p>
      </div>
    </div>

    <!-- Right Login Form Area -->
    <div class="login-right">
      <div class="login-form-wrapper">
        <div class="login-form-header">
          <h2 class="form-title">欢迎登录</h2>
          <p class="form-subtitle">请输入您的账号信息</p>
        </div>

        <a-form
          ref="formRef"
          :model="formState"
          :rules="rules"
          layout="vertical"
          class="login-form"
          @finish="handleLogin"
        >
          <a-form-item name="username">
            <a-input
              v-model:value="formState.username"
              size="large"
              placeholder="请输入用户名"
              class="login-input"
            >
              <template #prefix>
                <UserOutlined class="input-icon" />
              </template>
            </a-input>
          </a-form-item>

          <a-form-item name="password">
            <a-input-password
              v-model:value="formState.password"
              size="large"
              placeholder="请输入密码"
              class="login-input"
              @keyup.enter="handleLogin"
            >
              <template #prefix>
                <LockOutlined class="input-icon" />
              </template>
            </a-input-password>
          </a-form-item>

          <a-form-item>
            <div class="form-extra">
              <a-checkbox v-model:checked="rememberMe">记住我</a-checkbox>
              <a class="forgot-link">忘记密码</a>
            </div>
          </a-form-item>

          <a-form-item>
            <a-button
              type="primary"
              html-type="submit"
              size="large"
              block
              :loading="loading"
              class="login-btn"
            >
              登 录
            </a-button>
          </a-form-item>
        </a-form>

        <div class="login-footer">
          Copyright &copy; {{ currentYear }} YW Operations Team
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { useUserStore } from '@/store/user'
import type { Rule } from 'ant-design-vue/es/form'
import type { FormInstance } from 'ant-design-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const rememberMe = ref(false)
const currentYear = new Date().getFullYear()

const formState = reactive({
  username: '',
  password: '',
})

const rules: Record<string, Rule[]> = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  if (!formState.username || !formState.password) return
  loading.value = true
  try {
    await userStore.login(formState.username, formState.password)
    message.success('登录成功')
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (err: unknown) {
    const error = err as Error
    message.error(error.message || '登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  min-height: 100vh;
  background: #fff;
}

/* ===== Left Illustration ===== */
.login-left {
  flex: 0 0 60%;
  background: linear-gradient(135deg, #F5820D 0%, #FF6B35 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.left-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.deco-circle {
  position: absolute;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.15);
}

.deco-circle-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  right: -80px;
  background: rgba(255, 255, 255, 0.03);
}

.deco-circle-2 {
  width: 250px;
  height: 250px;
  bottom: 60px;
  left: -60px;
  background: rgba(255, 255, 255, 0.05);
}

.deco-circle-3 {
  width: 120px;
  height: 120px;
  top: 40%;
  right: 15%;
  background: rgba(255, 255, 255, 0.06);
}

.deco-dots {
  position: absolute;
  bottom: 20%;
  right: 10%;
  width: 120px;
  height: 120px;
  background-image: radial-gradient(rgba(255, 255, 255, 0.3) 2px, transparent 2px);
  background-size: 16px 16px;
}

.left-content {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 40px;
}

.brand-name {
  font-size: 56px;
  font-weight: 800;
  color: #fff;
  margin: 0 0 16px;
  letter-spacing: 2px;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.brand-subtitle {
  font-size: 22px;
  color: rgba(255, 255, 255, 0.95);
  margin: 0 0 12px;
  font-weight: 500;
}

.brand-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.75);
  margin: 0;
  letter-spacing: 1px;
}

/* ===== Right Login Form ===== */
.login-right {
  flex: 0 0 40%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: #fff;
}

.login-form-wrapper {
  width: 100%;
  max-width: 380px;
}

.login-form-header {
  margin-bottom: 40px;
}

.form-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px;
}

.form-subtitle {
  font-size: 14px;
  color: #999;
  margin: 0;
}

/* Form Inputs */
.login-form :deep(.ant-input-affix-wrapper) {
  border-radius: 8px;
  border-color: #e8e8e8;
  padding: 8px 12px;
}

.login-form :deep(.ant-input-affix-wrapper:hover),
.login-form :deep(.ant-input-affix-wrapper-focused) {
  border-color: #F5820D;
  box-shadow: 0 0 0 2px rgba(245, 130, 13, 0.1);
}

.input-icon {
  color: #bbb;
  font-size: 16px;
}

.form-extra {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.forgot-link {
  color: #F5820D;
  font-size: 13px;
}

.forgot-link:hover {
  color: #d4700b;
}

/* Login Button */
.login-btn {
  height: 44px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  background: #F5820D !important;
  border-color: #F5820D !important;
  box-shadow: 0 4px 12px rgba(245, 130, 13, 0.3);
  transition: all 0.3s;
}

.login-btn:hover {
  background: #d4700b !important;
  border-color: #d4700b !important;
  box-shadow: 0 6px 16px rgba(245, 130, 13, 0.4);
  transform: translateY(-1px);
}

/* Footer */
.login-footer {
  text-align: center;
  margin-top: 48px;
  color: #bbb;
  font-size: 13px;
}

/* ===== Responsive ===== */
@media (max-width: 992px) {
  .login-page {
    flex-direction: column;
  }

  .login-left {
    flex: none;
    min-height: 200px;
    padding: 40px 20px;
  }

  .brand-name {
    font-size: 36px;
  }

  .brand-subtitle {
    font-size: 16px;
  }

  .login-right {
    flex: 1;
    padding: 32px 24px;
  }
}

@media (max-width: 576px) {
  .login-left {
    display: none;
  }

  .login-right {
    flex: 1;
    min-height: 100vh;
  }

  .login-form-wrapper {
    max-width: 100%;
  }
}
</style>
