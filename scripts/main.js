import { world, BlockLocation } from "@minecraft/server";

// Хранилище активных буровых установок
const activeDrills = new Map();

// Регистрация блока буровой установки
world.events.beforeItemUseOn.subscribe((eventData) => {
  const player = eventData.source;
  const item = eventData.item;
  const blockLocation = eventData.blockLocation;
  
  if (item.id === "minecraft:iron_block") {
    // Создаем буровую установку
    const dimension = player.dimension;
    
    // Устанавливаем блок буровой установки
    dimension.getBlock(blockLocation).setType("minecraft:iron_block");
    
    player.sendMessage("§aБуровая установка установлена!");
    player.sendMessage("§eУстановка будет бурить на глубину 100-150 блоков");
    
    // Запускаем процесс бурения
    startDrilling(dimension, blockLocation, player);
  }
});

// Функция поиска ближайшего сундука
function findNearestChest(dimension, location, maxDistance = 10) {
  let nearestChest = null;
  let minDistance = maxDistance;
  
  // Ищем сундук в радиусе maxDistance блоков
  for (let x = -maxDistance; x <= maxDistance; x++) {
    for (let y = -maxDistance; y <= maxDistance; y++) {
      for (let z = -maxDistance; z <= maxDistance; z++) {
        const checkLocation = new BlockLocation(
          location.x + x,
          location.y + y,
          location.z + z
        );
        
        const block = dimension.getBlock(checkLocation);
        if (block.type.id === "minecraft:chest") {
          const distance = Math.sqrt(x*x + y*y + z*z);
          if (distance < minDistance) {
            minDistance = distance;
            nearestChest = checkLocation;
          }
        }
      }
    }
  }
  
  return nearestChest;
}

// Функция складывания предметов в сундук
function storeItemsInChest(dimension, chestLocation, items) {
  try {
    // Получаем сундук
    const chest = dimension.getBlockEntity(chestLocation);
    if (!chest) return false;
    
    // Складываем каждый предмет
    for (const item of items) {
      // Пытаемся добавить предмет в сундук
      const success = chest.addItem(item);
      if (!success) {
        // Если не поместился, выбрасываем рядом
        dimension.spawnItem(item, chestLocation);
      }
    }
    return true;
  } catch (error) {
    console.warn("Ошибка при складывании в сундук:", error);
    return false;
  }
}

// Функция бурения
function startDrilling(dimension, location, player) {
  const drillId = `${location.x}_${location.y}_${location.z}`;
  
  // Сообщаем о начале работы
  player.sendMessage("§aБуровая установка начала работу!");
  
  const drillInterval = setInterval(() => {
    try {
      // Проверяем, что блок все еще существует
      const block = dimension.getBlock(location);
      if (block.type.id !== "minecraft:iron_block") {
        clearInterval(drillInterval);
        activeDrills.delete(drillId);
        return;
      }
      
      // Определяем направление бурения (вниз)
      const drillLocation = new BlockLocation(
        location.x,
        location.y - 1,
        location.z
      );
      
      // Проверяем блок под установкой
      const targetBlock = dimension.getBlock(drillLocation);
      
      if (targetBlock.type.id !== "minecraft:air" && 
          targetBlock.type.id !== "minecraft:bedrock") {
        
        // Добываем ресурс
        const drops = getBlockDrops(targetBlock.type.id);
        
        // Удаляем блок
        targetBlock.setType("minecraft:air");
        
        // Ищем ближайший сундук
        const nearestChest = findNearestChest(dimension, location);
        
        if (nearestChest) {
          // Складываем в сундук
          const stored = storeItemsInChest(dimension, nearestChest, drops);
          if (stored) {
            player.sendMessage(`§aДобыто: ${drops.map(d => d.id).join(', ')} → Сложено в сундук`);
          } else {
            // Если не удалось сложить, выбрасываем рядом
            drops.forEach(drop => {
              dimension.spawnItem(drop, location);
            });
            player.sendMessage(`§eДобыто: ${drops.map(d => d.id).join(', ')} → Выброшено рядом`);
          }
        } else {
          // Если сундука нет, выбрасываем рядом
          drops.forEach(drop => {
            dimension.spawnItem(drop, location);
          });
          player.sendMessage(`§eДобыто: ${drops.map(d => d.id).join(', ')} → Выброшено рядом (сундук не найден)`);
        }
        
        // Эффекты
        dimension.spawnParticle("minecraft:blockcrack", location, {
          blockType: targetBlock.type.id
        });
        
        // Проверяем глубину
        const depth = location.y - drillLocation.y;
        if (depth >= 100) {
          player.sendMessage(`§6Глубина бурения: ${depth} блоков`);
        }
        
        // Останавливаем бурение на глубине 150 блоков
        if (depth >= 150) {
          player.sendMessage("§cДостигнута максимальная глубина (150 блоков)! Бурение остановлено.");
          clearInterval(drillInterval);
          activeDrills.delete(drillId);
          return;
        }
      }
      
    } catch (error) {
      console.warn("Ошибка в буровой установке:", error);
      player.sendMessage("§cОшибка в работе буровой установки!");
      clearInterval(drillInterval);
      activeDrills.delete(drillId);
    }
  }, 2000); // Бурение каждые 2 секунды
  
  // Сохраняем активную установку
  activeDrills.set(drillId, {
    interval: drillInterval,
    location: location,
    player: player
  });
  
  // Сообщаем о статусе
  player.sendMessage("§aБуровая установка активна и работает!");
}

// Функция получения дропа с блоков
function getBlockDrops(blockId) {
  const drops = [];
  
  switch (blockId) {
    case "minecraft:stone":
      drops.push({ id: "minecraft:cobblestone", count: 1 });
      break;
    case "minecraft:coal_ore":
      drops.push({ id: "minecraft:coal", count: 1 });
      break;
    case "minecraft:iron_ore":
      drops.push({ id: "minecraft:iron_ore", count: 1 });
      break;
    case "minecraft:gold_ore":
      drops.push({ id: "minecraft:gold_ore", count: 1 });
      break;
    case "minecraft:diamond_ore":
      drops.push({ id: "minecraft:diamond", count: 1 });
      break;
    case "minecraft:emerald_ore":
      drops.push({ id: "minecraft:emerald", count: 1 });
      break;
    case "minecraft:redstone_ore":
      drops.push({ id: "minecraft:redstone", count: 4 });
      break;
    case "minecraft:lapis_ore":
      drops.push({ id: "minecraft:lapis_lazuli", count: 4 });
      break;
    case "minecraft:ancient_debris":
      drops.push({ id: "minecraft:ancient_debris", count: 1 });
      break;
    case "minecraft:copper_ore":
      drops.push({ id: "minecraft:copper_ore", count: 1 });
      break;
    case "minecraft:deepslate_coal_ore":
      drops.push({ id: "minecraft:coal", count: 1 });
      break;
    case "minecraft:deepslate_iron_ore":
      drops.push({ id: "minecraft:iron_ore", count: 1 });
      break;
    case "minecraft:deepslate_gold_ore":
      drops.push({ id: "minecraft:gold_ore", count: 1 });
      break;
    case "minecraft:deepslate_diamond_ore":
      drops.push({ id: "minecraft:diamond", count: 1 });
      break;
    case "minecraft:deepslate_emerald_ore":
      drops.push({ id: "minecraft:emerald", count: 1 });
      break;
    case "minecraft:deepslate_redstone_ore":
      drops.push({ id: "minecraft:redstone", count: 4 });
      break;
    case "minecraft:deepslate_lapis_ore":
      drops.push({ id: "minecraft:lapis_lazuli", count: 4 });
      break;
    case "minecraft:deepslate_copper_ore":
      drops.push({ id: "minecraft:copper_ore", count: 1 });
      break;
    default:
      // Для других блоков просто добываем их как есть
      drops.push({ id: blockId, count: 1 });
  }
  
  return drops;
}

// Обработчик разрушения буровой установки
world.events.blockBreak.subscribe((eventData) => {
  const block = eventData.brokenBlockPermutation;
  const location = eventData.block.location;
  
  if (block.type.id === "minecraft:iron_block") {
    // Проверяем, является ли это буровой установкой
    const drillId = `${location.x}_${location.y}_${location.z}`;
    
    if (activeDrills.has(drillId)) {
      // Останавливаем бурение
      const drill = activeDrills.get(drillId);
      clearInterval(drill.interval);
      activeDrills.delete(drillId);
      
      eventData.player.sendMessage("§cБуровая установка разрушена! Бурение остановлено.");
    }
  }
});

// Команда для проверки статуса установок
world.events.beforeChat.subscribe((eventData) => {
  const message = eventData.message.toLowerCase();
  const player = eventData.sender;
  
  if (message === "!drill status" || message === "!дрилл статус") {
    if (activeDrills.size === 0) {
      player.sendMessage("§eАктивных буровых установок нет.");
    } else {
      player.sendMessage(`§aАктивных буровых установок: ${activeDrills.size}`);
      activeDrills.forEach((drill, id) => {
        const depth = Math.abs(drill.location.y - 64); // Примерная глубина
        player.sendMessage(`§7- Установка ${id}: глубина ~${depth} блоков`);
      });
    }
    eventData.cancel = true;
  }
  
  if (message === "!drill stop all" || message === "!дрилл стоп все") {
    let stopped = 0;
    activeDrills.forEach((drill, id) => {
      clearInterval(drill.interval);
      stopped++;
    });
    activeDrills.clear();
    player.sendMessage(`§aОстановлено ${stopped} буровых установок.`);
    eventData.cancel = true;
  }
});

console.log("§aМод 'Буровая установка' загружен!");
console.log("§eКоманды: !drill status, !drill stop all");