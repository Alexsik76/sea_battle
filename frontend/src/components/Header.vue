<script setup>
import { useGameStore } from '../stores/gameStore'

const store = useGameStore()
</script>

<template>
  <header class="h-[30vh] w-full flex flex-col items-center justify-center flex-initial px-4 text-center">
    <div class="mb-2">
      <h1 class="text-[min(6vh,36px)] font-black bg-gradient-to-r from-indigo-500 via-sky-400 to-indigo-500 bg-clip-text text-transparent uppercase tracking-widest leading-none">
        SEA BATTLE
      </h1>
    </div>
    
    <div v-if="store.gameState === 'playing'" class="flex justify-center items-center gap-8 text-[min(2.5vh,20px)] font-bold">
       <div class="flex flex-col items-center">
         <span class="text-sky-400 font-black drop-shadow-[0_0_8px_rgba(56,189,248,0.4)]">{{ store.userName || 'You' }}</span>
       </div>
       <div class="opacity-20 text-base font-normal">VS</div>
       <div class="flex flex-col items-center">
         <span class="text-rose-400 font-black drop-shadow-[0_0_8px_rgba(251,113,133,0.4)]">{{ store.opponentName }}</span>
       </div>
    </div>
    
    <div v-else-if="store.gameState === 'setup'" class="flex flex-col items-center gap-2">
      <h2 class="text-[min(3vh,24px)] font-bold text-white/80">Fleet Setup</h2>
      <div v-if="store.currentShipIndex < store.SHIPS_TO_PLACE.length" class="flex flex-col items-center">
        <div class="bg-sky-400/10 px-6 py-2 rounded-full border border-sky-400/20 text-sm">
          Place <b>{{ store.SHIPS_TO_PLACE[store.currentShipIndex].name }}</b> ({{ store.SHIPS_TO_PLACE[store.currentShipIndex].size }} cells)
        </div>
        <div class="text-[min(1.2vh,10px)] uppercase tracking-tighter opacity-40 mt-1">
          {{ store.finalizedShips.length }} / {{ store.SHIPS_TO_PLACE.length }} SHIPS DEPLOYED
        </div>
      </div>
    </div>
  </header>
</template>
