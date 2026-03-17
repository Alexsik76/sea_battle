import { useGameStore } from '../stores/gameStore'

export function usePlacement() {
  const store = useGameStore()

  const isValidPlacement = (x, y, currentCoords) => {
    // 1. Check adjacency to finalized ships (8 directions)
    for (let dx = -1; dx <= 1; dx++) {
      for (let dy = -1; dy <= 1; dy++) {
        const nx = x + dx, ny = y + dy
        if (nx >= 0 && nx < 10 && ny >= 0 && ny < 10) {
          if (store.finalizedShips.some(ship => ship.coords.some(c => c[0] === nx && c[1] === ny))) {
            return { valid: false, error: "Ships cannot touch each other!" }
          }
        }
      }
    }

    if (currentCoords.length === 0) return { valid: true }

    // 2. Check straight line and contiguity
    const nextCoords = [...currentCoords, [x, y]]
    const xs = nextCoords.map(c => c[0])
    const ys = nextCoords.map(c => c[1])

    const isHorizontal = ys.every(val => val === ys[0])
    const isVertical = xs.every(val => val === xs[0])

    if (!isHorizontal && !isVertical) {
      return { valid: false, error: "Ships must be in a straight line!" }
    }

    if (isHorizontal) {
      const minX = Math.min(...xs), maxX = Math.max(...xs)
      if (maxX - minX + 1 !== nextCoords.length) {
        return { valid: false, error: "Ships must be contiguous (no gaps)!" }
      }
    } else {
      const minY = Math.min(...ys), maxY = Math.max(...ys)
      if (maxY - minY + 1 !== nextCoords.length) {
        return { valid: false, error: "Ships must be contiguous (no gaps)!" }
      }
    }

    return { valid: true }
  }

  const autoPlaceShips = () => {
    // Clear any partial placement first
    if (store.currentShipCoords.length > 0) {
      store.currentShipCoords.forEach(c => store.board[c[1]][c[0]] = null)
      store.currentShipCoords = []
    }

    while (store.currentShipIndex < store.SHIPS_TO_PLACE.length) {
      const ship = store.SHIPS_TO_PLACE[store.currentShipIndex]
      let placed = false
      let attempts = 0
      
      while (!placed && attempts < 200) {
        attempts++
        const isHorizontal = Math.random() < 0.5
        const startX = Math.floor(Math.random() * (isHorizontal ? (11 - ship.size) : 10))
        const startY = Math.floor(Math.random() * (isHorizontal ? 10 : (11 - ship.size)))
        
        const coords = []
        let valid = true
        
        for (let i = 0; i < ship.size; i++) {
          const cx = isHorizontal ? startX + i : startX
          const cy = isHorizontal ? startY : startY + i
          
          const check = isValidPlacement(cx, cy, coords)
          if (!check.valid) {
            valid = false
            break
          }
          coords.push([cx, cy])
        }
        
        if (valid) {
          coords.forEach(c => store.board[c[1]][c[0]] = 'ship')
          store.finalizedShips.push({
            name: ship.name,
            size: ship.size,
            coords: coords
          })
          store.currentShipIndex++
          placed = true
        }
      }
      
      if (!placed) {
        store.errorMessage = "Could not place remaining ships. Try clearing or moving existing ones."
        return
      }
    }
    
    if (store.currentShipIndex === store.SHIPS_TO_PLACE.length) {
      store.placeShips(store.finalizedShips)
    }
  }

  return {
    isValidPlacement,
    autoPlaceShips
  }
}
