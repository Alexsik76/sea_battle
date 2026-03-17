<script setup>
import { useGameStore } from '../stores/gameStore'
import Lobby from './Lobby.vue'
import Board from './Board.vue'
import ProfileSetup from './ProfileSetup.vue'

const store = useGameStore()
</script>

<template>
  <main class="h-[50vh] w-full flex items-center justify-center min-h-0">
    <div v-if="store.gameState === 'setup'" class="h-full w-full flex items-center justify-center">
      <template v-if="store.currentShipIndex < store.SHIPS_TO_PLACE.length">
        <Board :setup="true" />
      </template>
      <div v-else class="flex flex-col items-center gap-4">
        <p class="text-emerald-400 font-bold text-xl animate-pulse uppercase tracking-widest">Fleet Ready</p>
        <div class="opacity-20 grayscale-[50%] scale-90">
            <Board :setup="false" :opponent="false" />
        </div>
      </div>
    </div>

    <div v-else-if="store.gameState === 'playing'" class="h-full w-full flex flex-wrap gap-8 sm:gap-24 justify-center items-center">
      <div class="flex flex-col items-center gap-2">
        <h3 class="text-[min(1.5vh,12px)] font-semibold opacity-30 uppercase tracking-[0.2em]">Defense</h3>
        <Board :opponent="false" />
      </div>
      <div class="flex flex-col items-center gap-2">
        <h3 class="text-[min(1.5vh,12px)] font-semibold opacity-30 uppercase tracking-[0.2em]">Offense</h3>
        <Board :opponent="true" />
      </div>
    </div>

    <div v-else class="max-h-full overflow-y-auto w-full flex justify-center py-4 px-4">
      <div v-if="!store.isProfileSet" class="card w-full max-w-md">
        <ProfileSetup />
      </div>
      <div v-else-if="store.gameState === 'lobby'" class="card w-full max-w-4xl">
        <div class="flex justify-between items-center px-4 py-2 mb-6 bg-white/5 rounded-lg text-lg">
          <span>Admiral <b class="text-sky-400">{{ store.userName || 'Unknown' }}</b></span>
          <button class="text-sky-400 bg-transparent p-0 text-sm hover:underline border-none outline-none cursor-pointer" @click="store.setUserName(null)">Change</button>
        </div>
        <Lobby />
      </div>
      <div v-else-if="store.gameState === 'waiting'" class="card p-12 flex flex-col items-center gap-6">
        <h2 class="text-2xl font-bold text-white uppercase tracking-widest">Searching Sector</h2>
        <div class="radar-scan"></div>
      </div>
      <div v-else-if="store.gameState === 'finished'" class="card p-12 text-center flex flex-col gap-6 items-center">
        <h2 class="text-xl opacity-60 uppercase tracking-widest">End of Battle</h2>
        <h1 :class="store.winner === store.playerId ? 'text-emerald-400' : 'text-rose-400'" class="text-6xl font-black drop-shadow-lg">
          {{ store.winner === store.playerId ? 'VICTORY' : 'DEFEAT' }}
        </h1>
        <button class="btn-primary mt-4" @click="store.leaveGame()">Back to Lobby</button>
      </div>
    </div>
  </main>
</template>
