<script setup>
import { ref } from 'vue'
import { useGameStore } from '../stores/gameStore'
import { useFocus } from '@vueuse/core'

const store = useGameStore()
const name = ref(store.userName)
const inputRef = ref(null)

useFocus(inputRef, { initialValue: true })

const handleSave = () => {
  store.setUserName(name.value.trim())
}
</script>

<template>
  <div class="flex flex-col gap-6 p-4">
    <h2 class="text-2xl font-bold">Welcome to Sea Battle</h2>
    <div class="flex flex-col gap-2 text-left">
      <label class="text-sm opacity-80">Enter your Admiral name:</label>
      <input 
        ref="inputRef"
        v-model="name" 
        type="text" 
        class="input-text"
        placeholder="Leave empty for default"
        @keyup.enter="handleSave"
      >
    </div>
    <button class="btn-primary w-full" @click="handleSave">
      Continue to Lobby
    </button>
  </div>
</template>

<style scoped>
/* No manual styles needed! */
</style>
