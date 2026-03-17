<script setup>
import { useGameStore } from '../stores/gameStore'
import { usePlacement } from '../composables/usePlacement'
import BoardCell from './BoardCell.vue'

const props = defineProps({
  setup: Boolean,
  opponent: Boolean
})

const store = useGameStore()
const { isValidPlacement, autoPlaceShips } = usePlacement()

const COLS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
const ROWS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

const handleCellClick = (x, y) => {
  if (props.setup) {
    const currentShip = store.SHIPS_TO_PLACE[store.currentShipIndex]
    if (!currentShip) return

    const coordIdx = store.currentShipCoords.findIndex(c => c[0] === x && c[1] === y)
    if (coordIdx !== -1) {
      store.currentShipCoords.forEach(c => store.board[c[1]][c[0]] = null)
      store.currentShipCoords = []
      store.errorMessage = null
      return
    }

    if (store.currentShipCoords.length < currentShip.size) {
      if (store.board[y][x] === null) {
        const result = isValidPlacement(x, y, store.currentShipCoords)
        if (!result.valid) {
          store.errorMessage = result.error
          return
        }
        store.errorMessage = null
        store.currentShipCoords.push([x, y])
        store.board[y][x] = 'ship'
      }
    }

    if (store.currentShipCoords.length === currentShip.size) {
      store.finalizedShips.push({
        name: currentShip.name,
        size: currentShip.size,
        coords: [...store.currentShipCoords]
      })
      store.currentShipCoords = []
      store.currentShipIndex++

      if (store.currentShipIndex === store.SHIPS_TO_PLACE.length) {
        store.placeShips(store.finalizedShips)
      }
    }
  } else if (props.opponent && store.isMyTurn) {
    if (store.opponentBoard[y][x] === null) {
      store.shoot(x, y)
    }
  }
}
</script>

<template>
  <div class="relative flex flex-col items-center">
    <!-- Board with Labels and Grid -->
    <div class="grid-board gap-[1px] bg-white/20 p-[1px] rounded-lg shadow-2xl overflow-hidden shrink-0 border border-white/10">
      
      <!-- Top-Left empty corner -->
      <div class="w-full h-full bg-[#0f172a]"></div>

      <!-- Top Labels (A-J) -->
      <div v-for="label in COLS" :key="label" class="flex items-center justify-center text-[min(1.2vh,12px)] font-black opacity-30 select-none bg-[#0f172a]">
        {{ label }}
      </div>

      <!-- Rows -->
      <template v-for="(rowLabel, yIdx) in ROWS" :key="'row-'+rowLabel">
        <!-- Side Label -->
        <div class="flex items-center justify-end pr-2 text-[min(1.2vh,12px)] font-black opacity-30 select-none bg-[#0f172a]">
          {{ rowLabel }}
        </div>

        <!-- Cells for this row -->
        <BoardCell 
          v-for="xIdx in 10" 
          :key="'cell-'+xIdx+'-'+yIdx"
          :x="xIdx-1"
          :y="yIdx"
          :opponent="props.opponent"
          :setup="props.setup"
          @click="handleCellClick"
        />
      </template>
    </div>

    <!-- Error Message Overlay -->
    <div v-if="store.errorMessage" class="absolute -bottom-8 left-0 right-0 text-rose-400 text-[min(1.2vh,10px)] font-bold z-10 text-center uppercase tracking-widest">
      {{ store.errorMessage }}
    </div>
  </div>
</template>

<style scoped>
/* No manual styles needed! */
</style>
