<script setup>
import { computed } from 'vue'
import { useGameStore } from '../stores/gameStore'

const props = defineProps({
  x: Number,
  y: Number,
  opponent: Boolean,
  setup: Boolean
})

const emit = defineEmits(['click'])

const store = useGameStore()

const cellValue = computed(() => 
  props.opponent ? store.opponentBoard[props.y][props.x] : store.board[props.y][props.x]
)

const isCurrentShip = computed(() => 
  !props.opponent && store.currentShipCoords.some(c => c[0] === props.x && c[1] === props.y)
)

const cellClass = computed(() => ({
  'w-full h-full flex items-center justify-center text-[min(2vh,16px)] transition-colors duration-200': true,
  'bg-slate-900/40': cellValue.value === null && !isCurrentShip.value,
  'bg-slate-600': cellValue.value === 'ship' && !isCurrentShip.value,
  'bg-sky-400 shadow-[0_0_8px_rgba(56,189,248,0.5)] z-5': isCurrentShip.value,
  'bg-rose-400/30': cellValue.value === 'hit',
  'bg-white/10': cellValue.value === 'miss',
  'hover:bg-sky-400/20 cursor-pointer': (props.setup && (cellValue.value === null || isCurrentShip.value)) || 
               (props.opponent && store.isMyTurn && cellValue.value === null)
}))

const handleClick = () => {
  emit('click', props.x, props.y)
}
</script>

<template>
  <div :class="cellClass" @click="handleClick">
    <template v-if="cellValue === 'hit'">💥</template>
    <template v-else-if="cellValue === 'miss'">·</template>
  </div>
</template>

<style scoped>
/* No manual styles needed! */
</style>
