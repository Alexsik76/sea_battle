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
      <div v-else-if="store.gameState === 'waiting'" class="card p-16 flex flex-col items-center gap-10 min-w-400px">
        <div class="relative w-48 h-48 flex items-center justify-center">
          <!-- Background Grid Rings -->
          <div class="absolute inset-0 border-2 border-sky-500/10 rounded-full"></div>
          <div class="absolute inset-4 border-2 border-sky-500/5 rounded-full"></div>
          <div class="absolute inset-12 border-2 border-sky-500/5 rounded-full"></div>
          
          <!-- Sonar Sweep -->
          <div class="radar-scan absolute inset-0 opacity-40"></div>
          
          <!-- Pulsing Ripples -->
          <div v-for="i in 3" :key="i"
            v-motion
            :initial="{ scale: 0.1, opacity: 0.8 }"
            :enter="{ 
              scale: 1.5, 
              opacity: 0,
              transition: { 
                duration: 3000, 
                repeat: Infinity,
                delay: i * 1000,
                ease: 'easeOut'
              } 
            }"
            class="absolute inset-0 border-2 border-sky-400 rounded-full"
          ></div>

          <!-- Random Blips (Scanning targets) -->
          <div v-for="i in 2" :key="'blip-'+i"
            v-motion
            :initial="{ opacity: 0, scale: 0 }"
            :enter="{ 
              opacity: [0, 1, 0],
              scale: [0.5, 1.2, 0.5],
              transition: { 
                duration: 2000, 
                repeat: Infinity,
                delay: i * 1500,
              } 
            }"
            class="absolute w-3 h-3 bg-rose-500 rounded-full shadow-[0_0_15px_#f43f5e]"
            :style="{ 
              top: i === 1 ? '30%' : '70%', 
              left: i === 1 ? '65%' : '25%' 
            }"
          ></div>

          <div class="z-10 text-sky-400 font-black text-xl tracking-[0.3em] animate-pulse">
            SCANNING
          </div>
        </div>

        <div class="flex flex-col items-center gap-3">
          <h2 class="text-2xl font-black text-white uppercase tracking-[0.5em] m-0">
            Searching Sector
          </h2>
          <div class="flex gap-2">
            <div v-for="i in 3" :key="'dot-'+i"
              v-motion
              :initial="{ y: 0 }"
              :enter="{ 
                y: -5,
                transition: { 
                  duration: 400, 
                  repeat: Infinity, 
                  repeatType: 'reverse',
                  delay: i * 150,
                } 
              }"
              class="w-2 h-2 bg-sky-400 rounded-full"
            ></div>
          </div>
          <p class="text-sm opacity-40 uppercase tracking-widest mt-2">Waiting for another Admiral to join</p>
        </div>
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
