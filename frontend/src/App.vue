<template>
  <a-config-provider :locale="zhCN" :theme="themeConfig">
    <router-view />
  </a-config-provider>
</template>

<script setup lang="ts">
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import type { ThemeConfig } from 'ant-design-vue/es/config-provider/context'

const themeConfig: ThemeConfig = {
  token: {
    colorPrimary: '#F5820D',
    colorLink: '#F5820D',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#f5222d',
    borderRadius: 6,
    colorBgLayout: '#f5f6fa',
  },
  components: {
    Menu: {
      darkItemBg: '#1a1a2e',
      darkSubMenuItemBg: '#16162a',
      darkItemSelectedBg: '#F5820D',
      darkItemHoverBg: 'rgba(245, 130, 13, 0.15)',
    },
    Button: {
      primaryShadow: '0 2px 8px rgba(245, 130, 13, 0.35)',
    },
  },
}
</script>

<style>
#app {
  width: 100%;
  height: 100%;
}

html,
body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* NProgress 进度条橙色 */
#nprogress .bar {
  background: #F5820D !important;
}
#nprogress .peg {
  box-shadow: 0 0 10px #F5820D, 0 0 5px #F5820D !important;
}
</style>
