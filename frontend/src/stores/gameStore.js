import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { useLocalStorage, useWebSocket } from '@vueuse/core'

export const useGameStore = defineStore('game', () => {
  // Persistence
  const gameId = useLocalStorage('sea_battle_game_id', null)
  const playerId = useLocalStorage('sea_battle_player_id', Math.random().toString(36).substring(7))
  const userName = useLocalStorage('sea_battle_user_name', '')
  
  if (gameId.value === 'null') gameId.value = null

  const isProfileSet = computed(() => userName.value !== null && userName.value !== '')
  const playerNames = ref({}) 
  const opponentName = computed(() => {
    const opponentId = Object.keys(playerNames.value).find(id => id !== playerId.value)
    return playerNames.value[opponentId] || 'Waiting...'
  })

  const gameState = ref('lobby')
  const isMyTurn = ref(false)
  const winner = ref(null)
  const lobbyGames = ref([])
  const errorMessage = ref(null)

  const board = ref(Array(10).fill().map(() => Array(10).fill(null)))
  const opponentBoard = ref(Array(10).fill().map(() => Array(10).fill(null)))

  const SHIPS_TO_PLACE = [
    { name: 'Battleship', size: 4 },
    { name: 'Cruiser 1', size: 3 }, { name: 'Cruiser 2', size: 3 },
    { name: 'Destroyer 1', size: 2 }, { name: 'Destroyer 2', size: 2 }, { name: 'Destroyer 3', size: 2 },
    { name: 'Submarine 1', size: 1 }, { name: 'Submarine 2', size: 1 }, { name: 'Submarine 3', size: 1 }, { name: 'Submarine 4', size: 1 }
  ]
  const currentShipIndex = ref(0)
  const currentShipCoords = ref([])
  const finalizedShips = ref([])

  // --- LOBBY (Still using VueUse as it's simple enough) ---
  const lobbyWsUrl = computed(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    return `${protocol}//${window.location.host}/ws/lobby`
  })
  const { data: lobbyData } = useWebSocket(lobbyWsUrl, { autoReconnect: true, heartbeat: false })
  watch(lobbyData, (newData) => {
    if (!newData) return
    try {
      const data = JSON.parse(newData)
      if (data.event === 'lobby_update') lobbyGames.value = data.games
    } catch (e) { console.error("Lobby parse error", e) }
  })

  // --- GAME SOCKET (Manual control for reliability) ---
  const socket = ref(null)
  const gameWsStatus = ref('CLOSED')

  function connect(gid) {
    const targetGid = gid || gameId.value
    if (!targetGid || targetGid === 'null') {
      gameId.value = null
      return
    }

    // Close existing socket if any
    if (socket.value) {
      socket.value.onclose = null // Prevent triggering disconnection logic
      socket.value.close()
    }

    gameId.value = targetGid
    errorMessage.value = null
    gameState.value = 'waiting' // Default state until sync
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${protocol}//${window.location.host}/ws/${targetGid}/${playerId.value}?name=${encodeURIComponent(userName.value)}`
    
    console.log("Connecting to Game WebSocket:", targetGid)
    gameWsStatus.value = 'CONNECTING'
    
    const ws = new WebSocket(url)
    socket.value = ws

    ws.onopen = () => {
      console.log("Game Socket Connected")
      gameWsStatus.value = 'OPEN'
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        handleMessage(data)
      } catch (e) { console.error("Message parse error", e) }
    }

    ws.onclose = (event) => {
      console.log("Game Socket Closed", event.code)
      gameWsStatus.value = 'CLOSED'
      socket.value = null
      
      // If server rejected (1008) or abnormal close (1006) on a specific game
      if (event.code === 1008 || event.code === 1006) {
        console.log("Game session invalid, returning to lobby")
        gameId.value = null
        gameState.value = 'lobby'
      } else if (gameId.value) {
        // Try to reconnect if we still have a gameId
        setTimeout(() => connect(), 2000)
      }
    }

    ws.onerror = (err) => {
      console.error("WebSocket Error:", err)
    }
  }

  // Auto-connect on startup
  if (gameId.value) {
    setTimeout(() => connect(), 500)
  }

  function handleMessage(data) {
    if (data.event === 'sync_state') {
      gameState.value = data.status
      if (data.board) board.value = data.board
      if (data.opponent_board) opponentBoard.value = data.opponent_board
      if (data.player_names) playerNames.value = data.player_names
      if (data.status === 'playing') isMyTurn.value = data.turn === playerId.value
      if (data.ships && data.ships.length > 0) {
          finalizedShips.value = data.ships
          currentShipIndex.value = SHIPS_TO_PLACE.length
      }
    } else if (data.event === 'game_setup') {
      gameState.value = 'setup'
      if (data.player_names) playerNames.value = data.player_names
    } else if (data.event === 'game_start') {
      gameState.value = 'playing'
      isMyTurn.value = data.turn === playerId.value
    } else if (data.event === 'move_made') {
      if (data.player_id === playerId.value) {
        opponentBoard.value[data.y][data.x] = data.is_hit ? 'hit' : 'miss'
      } else {
        board.value[data.y][data.x] = data.is_hit ? 'hit' : 'miss'
      }
      isMyTurn.value = data.next_turn === playerId.value
    } else if (data.event === 'game_over') {
      gameState.value = 'finished'
      winner.value = data.winner
      gameId.value = null
    } else if (data.event === 'error') {
      errorMessage.value = data.message
      if (data.message.includes('placement')) resetPlacement()
    } else if (data.event === 'player_joined') {
      if (data.name) playerNames.value[data.player_id] = data.name
    }
  }

  async function createGame(name) {
    const res = await fetch('/api/games/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, player_id: playerId.value, player_name: userName.value })
    })
    const data = await res.json()
    connect(data.game_id)
  }

  function setUserName(name) { userName.value = name }
  function resetPlacement() {
    currentShipIndex.value = 0
    currentShipCoords.value = []
    finalizedShips.value = []
    board.value = Array(10).fill().map(() => Array(10).fill(null))
    opponentBoard.value = Array(10).fill().map(() => Array(10).fill(null))
    errorMessage.value = null
  }
  function shoot(x, y) {
    if (!isMyTurn.value || !socket.value) return
    socket.value.send(JSON.stringify({ event: 'shoot', x, y }))
  }
  function placeShips(ships) {
    if (!socket.value) return
    socket.value.send(JSON.stringify({ event: 'place_ships', ships }))
  }
  function leaveGame() {
    gameId.value = null
    if (socket.value) {
      socket.value.close()
      socket.value = null
    }
    gameState.value = 'lobby'
    resetPlacement()
  }

  return {
    gameId, playerId, userName, isProfileSet, playerNames, gameState, board, opponentBoard, isMyTurn, winner, lobbyGames, errorMessage,
    SHIPS_TO_PLACE, currentShipIndex, currentShipCoords, finalizedShips, opponentName, gameWsStatus,
    connect, createGame, shoot, placeShips, resetPlacement, setUserName, leaveGame
  }
})
