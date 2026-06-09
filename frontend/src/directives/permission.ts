import type { Directive, DirectiveBinding } from 'vue'
import { useUserStore } from '@/store/user'

export const permissionDirective: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding<string>) {
    const permission = binding.value
    if (!permission) return

    const userStore = useUserStore()
    if (!userStore.hasPermission(permission)) {
      el.parentNode?.removeChild(el)
    }
  },
  updated(el: HTMLElement, binding: DirectiveBinding<string>) {
    const permission = binding.value
    if (!permission) return

    const userStore = useUserStore()
    if (!userStore.hasPermission(permission)) {
      el.parentNode?.removeChild(el)
    }
  },
}
