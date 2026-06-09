import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import App from './App.vue'
import router from './router'
import { permissionDirective } from './directives/permission'
import 'ant-design-vue/dist/reset.css'
import 'nprogress/nprogress.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Antd)

app.directive('permission', permissionDirective)

app.mount('#app')
