<script setup>
import { onMounted } from 'vue'
import { useGameStore } from './stores/gameStore'
import { usePlacement } from './composables/usePlacement'
import Lobby from './components/Lobby.vue'
import Board from './components/Board.vue'
import ProfileSetup from './components/ProfileSetup.vue'

const store = useGameStore()
const { autoPlaceShips } = usePlacement()

onMounted(() => {
  if (store.gameId) {
    store.connect()
  } else {
    store.connectToLobby()
  }
})

const getOpponentName = () => {
  const opponentId = Object.keys(store.playerNames).find(id => id !== store.playerId)
  return store.playerNames[opponentId] || 'Waiting...'
}
</script>

<template>
  <div class="h-screen max-h-screen flex flex-col items-center bg-[#0f172a] text-slate-200 overflow-hidden select-none px-4">
    
    <!-- Zone 1: Top (30vh) -->
    <div class="h-[30vh] w-full flex flex-col items-center justify-center flex-initial">
      <header class="mb-2">
        <h1 class="text-[min(6vh,36px)] font-black bg-gradient-to-r from-indigo-500 via-sky-400 to-indigo-500 bg-clip-text text-transparent uppercase tracking-widest leading-none">
          SEA BATTLE
        </h1>
      </header>
      
      <!-- Content depending on state -->
      <div v-if="store.gameState === 'playing'" class="flex justify-center items-center gap-8 text-[min(2.5vh,20px)] font-bold">
         <div class="flex flex-col items-center">
           <span class="text-sky-400 font-black drop-shadow-[0_0_8px_rgba(56,189,248,0.4)]">{{ store.userName || 'You' }}</span>
         </div>
         <div class="opacity-20 text-base font-normal">VS</div>
         <div class="flex flex-col items-center">
           <span class="text-rose-400 font-black drop-shadow-[0_0_8px_rgba(251,113,133,0.4)]">{{ getOpponentName() }}</span>
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
    </div>
    
    <!-- Zone 2: Middle (50vh) -->
    <div class="h-[50vh] w-full flex items-center justify-center min-h-0">
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
          <button class="btn-primary mt-4" @click="window.location.reload()">Back to Lobby</button>
        </div>
      </div>
    </div>
    
    <!-- Zone 3: Bottom (20vh) -->
    <div class="h-[20vh] w-full flex items-center justify-center flex-initial">
      <div v-if="store.gameState === 'playing'" class="text-center">
        <div :class="store.isMyTurn ? 'bg-sky-500/10 border-sky-500/30' : 'bg-white/5 border-white/10'" class="border px-10 py-3 rounded-full transition-all duration-500">
          <h3 :class="store.isMyTurn ? 'text-sky-400 drop-shadow-[0_0_10px_rgba(56,189,248,0.5)]' : 'opacity-30'" class="text-[min(2.5vh,20px)] font-black uppercase tracking-[0.4em] m-0">
            {{ store.isMyTurn ? "YOUR TURN" : "WAITING FOR OPPONENT" }}
          </h3>
        </div>
      </div>
      <div v-else-if="store.gameState === 'setup' && store.currentShipIndex < store.SHIPS_TO_PLACE.length" class="flex flex-col items-center gap-4">
        <button class="btn-success py-3 px-8 text-sm flex items-center gap-2 rounded-full font-black uppercase tracking-widest shadow-xl active:scale-95 transition-all" @click="autoPlaceShips">
          🎲 Randomize Fleet
        </button>
        <p class="text-[min(1.2vh,10px)] opacity-30 uppercase tracking-widest">Admiral, deploy your ships manually or use auto-resolve</p>
      </div>
    </div>

  </div>
</template>

<style scoped>
.radar-scan {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: 2px solid rgba(56, 189, 248, 0.3);
  position: relative;
  overflow: hidden;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.1) 0%, transparent 70%);
}

.radar-scan::after {
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  background: conic-gradient(from 0deg, #38bdf8 0deg, transparent 90deg);
  transform-origin: top left;
  animation: radar 2s linear infinite;
}

@keyframes radar {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
