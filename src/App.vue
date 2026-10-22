<script setup>
import { ref } from 'vue'

const privacyAcknowledged = ref(false)
</script>

<template>
  <main class="shell">
    <h1>在线聊天</h1>
    <p>临时音视频房间，支持桌面浏览器访问。</p>
    <label class="privacy">
      <input v-model="privacyAcknowledged" type="checkbox" />
      我已阅读隐私提示，了解媒体仅用于实时通话且不会被录制。
    </label>
    <button :disabled="!privacyAcknowledged" type="button">开始创建房间</button>
  </main>
</template>
