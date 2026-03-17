<script setup>
import { computed } from 'vue'
import { useGameStore } from '../stores/gameStore'

const props = defineProps({
  game: Object
})

const store = useGameStore()

const isMember = computed(() => (props.game.player_ids || []).includes(store.playerId))

const handleJoin = () => {
  store.connect(props.game.id)
}
</script>

<template>
  <div class="flex justify-between items-center p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors">
    <div class="text-left">
      <div class="font-bold text-lg text-sky-400">{{ game.name }}</div>
      <div class="text-sm opacity-80">
        Players: {{ game.players }}/2 ({{ game.online_players }} online)
        <span v-if="game.player_names.length" class="text-slate-400 ml-2">
          (Created by: {{ game.player_names[0] }})
        </span>
      </div>
    </div>
    
    <button 
      v-if="isMember" 
      class="btn-success text-sm py-2 px-4 shadow-none"
      @click="handleJoin"
    >
      Rejoin
    </button>
    <button 
      v-else-if="game.players < 2" 
      class="btn-primary text-sm py-2 px-4 shadow-none"
      @click="handleJoin"
    >
      Join Game
    </button>
    <div v-else class="py-2 px-4 bg-white/10 rounded text-xs text-slate-400">FULL</div>
  </div>
</template>

<style scoped>
/* No manual styles needed! */
</style>
