<script setup>
import { onMounted } from 'vue'
import { useGameStore } from './stores/gameStore'
import HeaderZone from './components/Header.vue'
import MainZone from './components/MainZone.vue'
import FooterZone from './components/Footer.vue'

const store = useGameStore()

onMounted(() => {
  if (store.gameId) {
    store.connect()
  } else {
    store.connectToLobby()
  }
})
</script>

<template>
  <div class="h-screen max-h-screen flex flex-col items-center bg-[#0f172a] text-slate-200 overflow-hidden select-none px-4">
    <HeaderZone />
    <MainZone />
    <FooterZone />
  </div>
</template>
