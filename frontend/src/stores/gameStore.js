import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useGameStore = defineStore('game', () => {
  const savedGameId = localStorage.getItem('sea_battle_game_id')
  const gameId = ref(savedGameId || null)
  
  // Persist playerId in localStorage
  const savedPlayerId = localStorage.getItem('sea_battle_player_id')
  const initialPlayerId = savedPlayerId || Math.random().toString(36).substring(7)
  if (!savedPlayerId) localStorage.setItem('sea_battle_player_id', initialPlayerId)
  
  const playerId = ref(initialPlayerId)
  const savedUserName = localStorage.getItem('sea_battle_user_name')
  const userName = ref(savedUserName || '')
  const isProfileSet = computed(() => userName.value !== null && userName.value !== '')
  const playerNames = ref({}) // id -> name
  const opponentName = computed(() => {
    const opponentId = Object.keys(playerNames.value).find(id => id !== playerId.value)
    return playerNames.value[opponentId] || 'Waiting...'
  })

  const gameState = ref('lobby') // lobby, setup, playing, finished
  const socket = ref(null)
  const lobbySocket = ref(null)

  const board = ref(Array(10).fill().map(() => Array(10).fill(null)))
  const opponentBoard = ref(Array(10).fill().map(() => Array(10).fill(null)))
  const isMyTurn = ref(false)
  const winner = ref(null)
  const lobbyGames = ref([])
  const errorMessage = ref(null)

  // Ship placement state
  const SHIPS_TO_PLACE = [
    { name: 'Battleship', size: 4 },
    { name: 'Cruiser 1', size: 3 }, { name: 'Cruiser 2', size: 3 },
    { name: 'Destroyer 1', size: 2 }, { name: 'Destroyer 2', size: 2 }, { name: 'Destroyer 3', size: 2 },
    { name: 'Submarine 1', size: 1 }, { name: 'Submarine 2', size: 1 }, { name: 'Submarine 3', size: 1 }, { name: 'Submarine 4', size: 1 }
  ]
  const currentShipIndex = ref(0)
  const currentShipCoords = ref([])
  const finalizedShips = ref([])

  function setUserName(name) {
    userName.value = name
    if (name === null) {
      localStorage.removeItem('sea_battle_user_name')
    } else {
      localStorage.setItem('sea_battle_user_name', name)
    }
  }

  function resetPlacement() {
    currentShipIndex.value = 0
    currentShipCoords.value = []
    finalizedShips.value = []
    board.value = Array(10).fill().map(() => Array(10).fill(null))
    opponentBoard.value = Array(10).fill().map(() => Array(10).fill(null))
    errorMessage.value = null
  }

  function connectToLobby() {
    if (lobbySocket.value) return
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const wsUrl = `${protocol}//${host}/ws/lobby`
    
    lobbySocket.value = new WebSocket(wsUrl)
    lobbySocket.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.event === 'lobby_update') {
        lobbyGames.value = data.games
      }
    }
    lobbySocket.value.onclose = () => {
      lobbySocket.value = null
      setTimeout(connectToLobby, 3000)
    }
  }

  function connect(gid) {
    if (gid) {
      gameId.value = gid
      localStorage.setItem('sea_battle_game_id', gid)
    }
    const currentGid = gid || gameId.value
    if (!currentGid) return

    errorMessage.value = null
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const wsUrl = `${protocol}//${host}/ws/${currentGid}/${playerId.value}?name=${encodeURIComponent(userName.value)}`
    
    socket.value = new WebSocket(wsUrl)
    socket.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleMessage(data)
    }
    socket.value.onclose = (event) => {
      socket.value = null
      // 1008 is our "Game not found" or "Game Error" code
      if (event.code === 1008) {
        localStorage.removeItem('sea_battle_game_id')
        gameId.value = null
        gameState.value = 'lobby'
        connectToLobby()
      } else if (gameId.value && gameState.value !== 'finished') {
        // Try to reconnect if the game is still active
        setTimeout(() => connect(), 3000)
      }
    }
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
      localStorage.removeItem('sea_battle_game_id')
    } else if (data.event === 'error') {
      errorMessage.value = data.message
      if (data.message.includes('placement')) resetPlacement()
    } else if (data.event === 'player_joined') {
      if (data.name) playerNames.value[data.player_id] = data.name
    }
  }

  async function fetchGames() {
    const res = await fetch('/api/games')
    lobbyGames.value = await res.json()
  }

  async function createGame(name) {
    const res = await fetch('/api/games/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
          name, 
          player_id: playerId.value, 
          player_name: userName.value 
      })
    })
    const data = await res.json()
    connect(data.game_id)
  }

  function shoot(x, y) {
    if (!isMyTurn.value) return
    socket.value.send(JSON.stringify({ event: 'shoot', x, y }))
  }

  function placeShips(ships) {
    socket.value.send(JSON.stringify({ event: 'place_ships', ships }))
  }

  function leaveGame() {
    if (socket.value) {
      socket.value.close()
      socket.value = null
    }
    gameId.value = null
    localStorage.removeItem('sea_battle_game_id')
    gameState.value = 'lobby'
    resetPlacement()
    connectToLobby()
  }

  return {
    gameId, playerId, userName, isProfileSet, playerNames, gameState, board, opponentBoard, isMyTurn, winner, lobbyGames, errorMessage,
    SHIPS_TO_PLACE, currentShipIndex, currentShipCoords, finalizedShips, opponentName,
    connect, connectToLobby, fetchGames, createGame, shoot, placeShips, resetPlacement, setUserName, leaveGame
  }
  })

