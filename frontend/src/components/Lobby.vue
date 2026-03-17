<script setup>
import { ref } from 'vue'
import { useGameStore } from '../stores/gameStore'
import { useFocus } from '@vueuse/core'
import GameListItem from './GameListItem.vue'

const store = useGameStore()
const newGameName = ref('')
const inputRef = ref(null)

useFocus(inputRef, { initialValue: true })

const handleCreate = () => {
  if (newGameName.value.trim()) {
    store.createGame(newGameName.value.trim())
    newGameName.value = ''
  }
}
</script>

<template>
  <div class="flex flex-col gap-8 w-full max-w-500px">
    <section class="flex flex-col gap-4">
      <h3 class="text-lg font-bold">Create New Game</h3>
      <div class="flex gap-2">
        <input ref="inputRef" v-model="newGameName" class="input-text flex-1" placeholder="Game Name" @keyup.enter="handleCreate">
        <button class="btn-primary" @click="handleCreate" :disabled="!newGameName.trim()">Create</button>
      </div>
    </section>

    <section class="flex flex-col gap-4">
      <h3 class="text-lg font-bold">Active Games</h3>
      <div v-if="store.lobbyGames.length === 0" class="p-8 text-center opacity-50 italic">
        No games available. Be the first to start!
      </div>
      <div class="flex flex-col gap-3">
        <GameListItem 
          v-for="game in store.lobbyGames" 
          :key="game.id" 
          :game="game" 
        />
      </div>
    </section>
  </div>
</template>

<style scoped>
/* No manual styles needed! */
</style>
