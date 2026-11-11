<script setup lang="ts">
import { currentLocale, toggleLocale } from '../state/i18n'
</script>

<template>
  <button
    type="button"
    class="lang-switch-btn"
    :title="currentLocale === 'vi' ? 'Chuyển sang English' : 'Switch to Tiếng Việt'"
    @click="toggleLocale"
  >
    <span class="lang-flag">{{ currentLocale === 'vi' ? '🇻🇳 VI' : '🇬🇧 EN' }}</span>
  </button>
</template>

<style scoped>
.lang-switch-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(120, 120, 120, 0.1);
  border: 1px solid rgba(120, 120, 120, 0.2);
  border-radius: 999px;
  padding: 4px 10px;
  font-family: inherit;
  font-size: 12px;
  font-weight: 600;
  color: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}
.lang-switch-btn:hover {
  background: rgba(120, 120, 120, 0.2);
  transform: translateY(-1px);
}
.lang-flag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
</style>

