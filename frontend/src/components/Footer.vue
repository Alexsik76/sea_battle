<script setup>
import { useGameStore } from '../stores/gameStore'
import { usePlacement } from '../composables/usePlacement'

const store = useGameStore()
const { autoPlaceShips } = usePlacement()
</script>

<template>
  <footer class="h-[20vh] w-full flex items-center justify-center flex-initial">
    <div v-if="store.gameState === 'playing'" class="text-center">
      <div :class="store.isMyTurn ? 'bg-sky-500/10 border-sky-500/30' : 'bg-white/5 border-white/10'" class="border px-10 py-3 rounded-full transition-all duration-500">
        <h3 :class="store.isMyTurn ? 'text-sky-400 drop-shadow-[0_0_10px_rgba(56,189,248,0.5)]' : 'opacity-30'" class="text-[min(2.5vh,20px)] font-black uppercase tracking-[0.4em] m-0">
          {{ store.isMyTurn ? "YOUR TURN" : "WAITING FOR OPPONENT" }}
        </h3>
      </div>
    </div>
    <div v-else-if="store.gameState === 'setup' && store.currentShipIndex < store.SHIPS_TO_PLACE.length" class="flex flex-col items-center gap-4">
      <button class="btn-success py-3 px-8 text-sm flex items-center gap-2 rounded-full font-black uppercase tracking-widest shadow-xl" @click="autoPlaceShips">
        🎲 Randomize Fleet
      </button>
      <p class="text-[min(1.2vh,10px)] opacity-30 uppercase tracking-widest">Admiral, deploy your ships manually or use auto-resolve</p>
    </div>
  </footer>
</template>
